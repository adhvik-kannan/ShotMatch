import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Alert, 
  ScrollView, 
  Image, 
  ActivityIndicator 
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as VideoThumbnails from 'expo-video-thumbnails';
import * as FileSystem from 'expo-file-system';
import Constants from 'expo-constants';

interface VideoData {
  videoUri: string;
  thumbnailUri: string;
  base64Data?: string;
}

interface ConsistencyUploadProps {
  navigation: any;
}

const frontExampleImages = [
  'https://photo-cdn2.icons8.com/PBC4NhdxYUzJOkCgAcR9S9YwQHW8eCETrTRwbZrmCCI/rs:fit:576:864/czM6Ly9pY29uczgu/bW9vc2UtcHJvZC5h/c3NldHMvYXNzZXRz/L3NhdGEvb3JpZ2lu/YWwvMzcyLzQ0Nzkx/ZWNjLWU4ODEtNDc0/NS05ODEyLTg1YTg0/YjE2ZWRjMi5qcGc.webp'
];

const sideExampleImages = [
  'https://masterwiki.how/_nuxt/84e4edf90c002a0670e45038ac95bdd0-300.jpg'
];

const Consistency: React.FC<ConsistencyUploadProps> = ({ navigation }) => {
  const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
  const [frontVideos, setFrontVideos] = useState<VideoData[]>([]);
  const [sideVideos, setSideVideos] = useState<VideoData[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      setPermissionGranted(status === 'granted');
    })();
  }, []);

  const pickVideos = async (angle: 'front' | 'side') => {
    if (!permissionGranted) {
      Alert.alert('Permission to access media library is required!');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      allowsMultipleSelection: true,
      quality: 1,
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
      if (angle === 'front') {
        const newVideos = frontVideos.concat(selectedVideos);
        if (newVideos.length > 5) {
          Alert.alert('Error', 'You can only upload up to 5 front view videos.');
          return;
        }
        setFrontVideos(newVideos);
      } else {
        const newVideos = sideVideos.concat(selectedVideos);
        if (newVideos.length > 5) {
          Alert.alert('Error', 'You can only upload up to 5 side view videos.');
          return;
        }
        setSideVideos(newVideos);
      }
    }
  };

  const uploadVideosHandler = async () => {
    // Check that the same number of front and side videos have been uploaded
    if (frontVideos.length !== sideVideos.length) {
      Alert.alert('Error', 'Please upload the same number of front and side view videos.');
      return;
    }
    // Ensure at least two videos are selected for each angle
    if (frontVideos.length < 2 || sideVideos.length < 2) {
      Alert.alert('Error', 'Please upload at least two front and two side view videos.');
      return;
    }
    setUploading(true);
    try {
      // Convert videos to base64
      const convertVideos = async (videos: VideoData[]): Promise<VideoData[]> => {
        return Promise.all(
          videos.map(async video => {
            const base64Data = await FileSystem.readAsStringAsync(video.videoUri, {
              encoding: FileSystem.EncodingType.Base64,
            });
            return { ...video, base64Data };
          })
        );
      };

      const convertedFrontVideos = await convertVideos(frontVideos);
      const convertedSideVideos = await convertVideos(sideVideos);

      const payload = {
        frontVideos: convertedFrontVideos,
        sideVideos: convertedSideVideos,
      };

      const backendUrl: string = Constants.expoConfig?.extra?.backendUrl;
      const response = await fetch(`http://${backendUrl}:5000/process_consistency_videos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Consistency videos processed successfully!');
        navigation.navigate('ConsistencyResults');
      } else {
        Alert.alert('Error', 'Failed to process consistency videos.');
        navigation.navigate('Consistency');
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'An error occurred while uploading videos.');
      navigation.navigate('Consistency');
    } finally {
      setUploading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Upload Your Consistency Videos</Text>
      
      <Text style={styles.instruction}>Please upload your front view videos (up to 5).</Text>
      <View style={styles.exampleImageContainer}>
        {frontExampleImages.map((uri, index) => (
          <Image 
            key={index} 
            source={{ uri }} 
            style={styles.exampleImage}
            resizeMode="contain"
          />
        ))}
      </View>
      <TouchableOpacity style={styles.uploadButton} onPress={() => pickVideos('front')}>
        <Text style={styles.buttonText}>Select Front View Videos</Text>
      </TouchableOpacity>
      <ScrollView horizontal contentContainerStyle={styles.thumbnailContainer}>
        {frontVideos.map((video, index) => (
          <Image key={index} source={{ uri: video.thumbnailUri }} style={styles.thumbnail} />
        ))}
      </ScrollView>

      <Text style={styles.instruction}>Now upload your side view videos (up to 5).</Text>
      <View style={styles.exampleImageContainer}>
        {sideExampleImages.map((uri, index) => (
          <Image 
            key={index} 
            source={{ uri }} 
            style={styles.exampleImage}
            resizeMode="contain"
          />
        ))}
      </View>
      <TouchableOpacity style={styles.uploadButton} onPress={() => pickVideos('side')}>
        <Text style={styles.buttonText}>Select Side View Videos</Text>
      </TouchableOpacity>
      <ScrollView horizontal contentContainerStyle={styles.thumbnailContainer}>
        {sideVideos.map((video, index) => (
          <Image key={index} source={{ uri: video.thumbnailUri }} style={styles.thumbnail} />
        ))}
      </ScrollView>

      <TouchableOpacity 
        style={styles.uploadButton} 
        onPress={uploadVideosHandler}
        disabled={uploading}
      >
        {uploading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Upload Consistency Videos</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20,
    paddingVertical: 30,
    backgroundColor: '#F5F5F5',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 20,
  },
  instruction: {
    fontSize: 16,
    marginVertical: 10,
    textAlign: 'center',
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
    flexDirection: 'row',
    marginVertical: 10,
    alignItems: 'center',
  },
  thumbnail: {
    width: 120,
    height: 90,
    marginRight: 10,
    borderRadius: 4,
  },
});

export default Consistency;
