import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Image,
  ActivityIndicator,
  Platform
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as VideoThumbnails from 'expo-video-thumbnails';
import { useRoute, RouteProp } from '@react-navigation/native';

type Player = {
  name: string;
  image: string;
};

type RootStackParamList = {
  UploadVideos: { selectedPlayer: Player; user: string };
};

type UploadVideosRouteProp = RouteProp<RootStackParamList, 'UploadVideos'>;

interface VideoData {
  videoUri: string;
  thumbnailUri: string;
}

interface HomeProps {
  navigation: any;
}

const frontExampleImages = [
  'https://photo-cdn2.icons8.com/PBC4NhdxYUzJOkCgAcR9S9YwQHW8eCETrTRwbZrmCCI/rs:fit:576:864/czM6Ly9pY29uczgu/bW9vc2UtcHJvZC5h/c3NldHMvYXNzZXRz/L3NhdGEvb3JpZ2lu/YWwvMzcyLzQ0Nzkx/ZWNjLWU4ODEtNDc0/NS05ODEyLTg1YTg0/YjE2ZWRjMi5qcGc.webp'
];

const sideExampleImages = [
  'https://masterwiki.how/_nuxt/84e4edf90c002a0670e45038ac95bdd0-300.jpg'
];

const UploadVideos: React.FC<HomeProps> = ({ navigation }) => {
  const route = useRoute<UploadVideosRouteProp>();
  const { selectedPlayer, user } = route.params;

  // Instead of arrays, we now store one video per angle (or null if not selected)
  const [frontVideo, setFrontVideo] = useState<VideoData | null>(null);
  const [sideVideo, setSideVideo] = useState<VideoData | null>(null);
  const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);

  useEffect(() => {
    (async () => {
      if (Platform.OS !== 'web') {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        setPermissionGranted(status === 'granted');
      }
    })();
  }, []);

  const pickVideo = async (angle: 'front' | 'side') => {
    if (!permissionGranted) {
      Alert.alert('Permission to access media library is required!');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      allowsEditing: false,
      quality: 1,
      allowsMultipleSelection: false, // only one video at a time
      selectionLimit: 1,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      const asset = result.assets[0];
      try {
        const thumbnailResult = await VideoThumbnails.getThumbnailAsync(asset.uri, { time: 1000 });
        const videoData: VideoData = {
          videoUri: asset.uri,
          thumbnailUri: thumbnailResult.uri,
        };
        if (angle === 'front') {
          setFrontVideo(videoData);
        } else {
          setSideVideo(videoData);
        }
      } catch (e) {
        console.warn(e);
        Alert.alert('Error', 'Failed to generate thumbnail.');
      }
    }
  };

  const uploadVideos = () => {
    if (frontVideo && sideVideo) {
      // Upload logic here. For example, navigate to next screen or call API.
      Alert.alert('Uploading videos...');
      navigation.navigate('ProcessVideos', { videos: [frontVideo, sideVideo], selectedPlayer, user });
    } else {
      Alert.alert('Error', 'Please select one front view and one side view video.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Top Section: Player's Image and Name */}
      <View style={styles.topContainer}>
        <Image source={{ uri: selectedPlayer.image }} style={styles.playerImage} />
      </View>
      <Text style={styles.playerName}>{selectedPlayer.name}</Text>

      {/* Upload Section */}
      <Text style={styles.title}>Upload Your Videos</Text>
      <Text style={styles.instruction}>Please select one front view and one side view video for analysis.</Text>

      {/* Front View Section */}
      <Text style={styles.instruction}>Front View (Example):</Text>
      <View style={styles.exampleImageContainer}>
        {frontExampleImages.map((uri, index) => (
          <Image key={index} source={{ uri }} style={styles.exampleImage} resizeMode="contain" />
        ))}
      </View>
      <TouchableOpacity style={styles.uploadButton} onPress={() => pickVideo('front')}>
        <Text style={styles.buttonText}>Select Front View Video</Text>
      </TouchableOpacity>
      {frontVideo && (
        <View style={styles.thumbnailContainer}>
          <Image source={{ uri: frontVideo.thumbnailUri }} style={styles.thumbnail} />
        </View>
      )}

      {/* Side View Section */}
      <Text style={styles.instruction}>Side View (Example):</Text>
      <View style={styles.exampleImageContainer}>
        {sideExampleImages.map((uri, index) => (
          <Image key={index} source={{ uri }} style={styles.exampleImage} resizeMode="contain" />
        ))}
      </View>
      <TouchableOpacity style={styles.uploadButton} onPress={() => pickVideo('side')}>
        <Text style={styles.buttonText}>Select Side View Video</Text>
      </TouchableOpacity>
      {sideVideo && (
        <View style={styles.thumbnailContainer}>
          <Image source={{ uri: sideVideo.thumbnailUri }} style={styles.thumbnail} />
        </View>
      )}

      <TouchableOpacity style={styles.uploadButton} onPress={uploadVideos} disabled={uploading}>
        {uploading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Upload Videos</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 30,
    paddingHorizontal: 20,
    backgroundColor: '#F5F5F5',
  },
  topContainer: {
    width: '100%',
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eee',
    marginBottom: 10,
  },
  playerImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  playerName: {
    textAlign: 'center',
    fontSize: 22,
    fontWeight: '600',
    marginVertical: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
    marginVertical: 20,
  },
  instruction: {
    fontSize: 16,
    textAlign: 'center',
    marginVertical: 10,
  },
  exampleImageContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 10,
  },
  exampleImage: {
    width: 300,
    height: 200,
    marginHorizontal: 5,
    borderRadius: 8,
  },
  uploadButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  thumbnailContainer: {
    alignItems: 'center',
    marginVertical: 10,
  },
  thumbnail: {
    width: 300,
    height: 200,
    borderRadius: 8,
  },
});

export default UploadVideos;