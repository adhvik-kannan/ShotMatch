import React, { useState, useEffect } from 'react';
import {
  View,
  Button,
  StyleSheet,
  Platform,
  Image,
  Text,
  Alert,
  ScrollView,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as VideoThumbnails from 'expo-video-thumbnails';
import { useRoute, RouteProp } from '@react-navigation/native';

type Player = {
  name: string;
  image: string;
};

type RootStackParamList = {
  UploadVideos: { selectedPlayer: Player };
};

type UploadVideosRouteProp = RouteProp<RootStackParamList, 'UploadVideos'>;

interface VideoData {
  videoUri: string;
  thumbnailUri: string;
}

interface HomeProps {
  navigation: any;
}

const UploadVideos: React.FC<HomeProps> = ({ navigation }) => {
  const route = useRoute<UploadVideosRouteProp>();
  const { selectedPlayer } = route.params;

  const [videos, setVideos] = useState<VideoData[]>([]);
  const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
  const [containerHeight, setContainerHeight] = useState<number>(0);

  useEffect(() => {
    (async () => {
      if (Platform.OS !== 'web') {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        setPermissionGranted(status === 'granted');
      }
    })();
  }, []);

  const pickVideos = async () => {
    if (!permissionGranted) {
      Alert.alert('Permission to access media library is required!');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      allowsEditing: false,
      quality: 1,
      allowsMultipleSelection: true,
      selectionLimit: 2,
    });

    if (!result.canceled && result.assets) {
      const selectedVideos: VideoData[] = [];
      for (const asset of result.assets) {
        try {
          const thumbnailResult = await VideoThumbnails.getThumbnailAsync(asset.uri, { time: 1000 });
          selectedVideos.push({
            videoUri: asset.uri,
            thumbnailUri: thumbnailResult.uri,
          });
        } catch (e) {
          console.warn(e);
        }
      }
      setVideos(selectedVideos);
    }
  };

  const uploadVideos = () => {
    if (videos.length > 0) {
      Alert.alert('Uploading videos...');
      navigation.navigate('ProcessVideos', { videos, selectedPlayer });
      // Insert your upload logic here.
    } else {
      Alert.alert('No videos selected to upload!');
    }
  };

  return (
    <View style={styles.container}>
      {/* Top Section: Player's Image */}
      <View style={styles.topContainer}>
        <Image source={{ uri: selectedPlayer.image }} style={styles.playerImage} />
      </View>
      <Text style={styles.playerName}>{selectedPlayer.name}</Text>

      {/* Bottom Section: Buttons and Video Display Area */}
      <View style={styles.bottomContainer}>
        {videos.length > 0 ? (
          <View style={styles.buttonsRow}>
            <View style={styles.buttonWrapper}>
              <Button title="Upload" onPress={uploadVideos} />
            </View>
            <View style={styles.buttonWrapper}>
              <Button title="Select Different Videos" onPress={pickVideos} />
            </View>
          </View>
        ) : (
          <Button title="Select Video" onPress={pickVideos} />
        )}

        {videos.length > 0 && (
          <View
            style={styles.videoDisplayContainer}
            onLayout={(event) => {
              const { height } = event.nativeEvent.layout;
              setContainerHeight(height);
            }}
          >
            <ScrollView
              pagingEnabled
              showsVerticalScrollIndicator
              style={styles.videoScrollView}
              contentContainerStyle={styles.videoScrollContent}
            >
              {videos.map((item, index) => (
                <View key={index} style={[styles.videoItem, { height: containerHeight }]}>
                  <Image source={{ uri: item.thumbnailUri }} style={styles.videoImage} />
                </View>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  topContainer: {
    width: '100%',
    maxHeight: 200, // Increase if you want the top area a bit larger
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eee',
  },
  playerImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain', // Ensures the full image is visible
  },
  playerName: {
    textAlign: 'center',
    fontSize: 20,
    fontWeight: '600',
    marginVertical: 10,
  },
  bottomContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  buttonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  buttonWrapper: {
    flex: 1,
    marginHorizontal: 5,
  },
  videoDisplayContainer: {
    flex: 1, // Fills the remaining space under the buttons
  },
  videoScrollView: {
    flex: 1,
  },
  videoScrollContent: {
    flexGrow: 1,
  },
  videoItem: {
    width: '100%',
    // The height is set dynamically via containerHeight
  },
  videoImage: {
    flex: 1,
    width: '100%',
    resizeMode: 'cover', // Use 'contain' if you prefer letterboxing
  },
});

export default UploadVideos;
