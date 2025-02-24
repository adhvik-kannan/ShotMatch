import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import Constants from 'expo-constants';
import * as FileSystem from 'expo-file-system';

type VideoData = {
  videoUri: string;
  thumbnailUri: string;
  // Will add a base64 field after conversion
  base64Data?: string;
};

type RootStackParamList = {
  ProcessVideos: { videos: VideoData[]; selectedPlayer: any };
};

type ProcessVideosRouteProp = RouteProp<RootStackParamList, 'ProcessVideos'>;

interface HomeProps {
  navigation: any;
}

const ProcessVideos: React.FC<HomeProps> = ({ navigation }) => {
  const route = useRoute<ProcessVideosRouteProp>();
  const { videos, selectedPlayer } = route.params;

  const [processing, setProcessing] = useState<boolean>(true);
  const [message, setMessage] = useState<string>('Processing Videos...');

  useEffect(() => {
    const sendVideos = async () => {
      try {
        // Convert local video files to base64 strings
        const convertedVideos = await Promise.all(
          videos.map(async (video) => {
            const base64Data = await FileSystem.readAsStringAsync(video.videoUri, {
              encoding: FileSystem.EncodingType.Base64,
            });
            return { ...video, base64Data };
          })
        );
        // console.log('Converted Videos:', convertedVideos);

        const backendUrl: string = Constants.expoConfig?.extra?.backendUrl;
        console.log('Backend URL:', backendUrl);
        const response = await fetch(`http://${backendUrl}:5000/process_videos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ videos: convertedVideos }),
        });
        if (response.ok) {
          const jsonData = await response.json();
          // console.log('Response from backend:', jsonData);
          const dummyMetrics = [
            { metric: 'Points', you: 25, player: 30 },
            { metric: 'Assists', you: 7, player: 5 },
            { metric: 'Rebounds', you: 10, player: 8 },
            // Add more metric rows as needed
          ];
          setMessage('Videos processed successfully!');
          setTimeout(() => {
            navigation.navigate('PerformanceMetrics', {
              metrics: dummyMetrics,
              selectedPlayer: selectedPlayer,
            });
          }, 1000);
        } else {
          setMessage('Failed to process videos.');
          setTimeout(() => {
            navigation.navigate('UploadVideos', { selectedPlayer: selectedPlayer });
          }, 1500);
        }
      } catch (error) {
        console.error(error);
        setMessage('Error processing videos.');
        setTimeout(() => {
          navigation.navigate('UploadVideos', { selectedPlayer: selectedPlayer });
        }, 1500);
      } finally {
        setProcessing(false);
      }
    };

    sendVideos();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.message}>{message}</Text>
      {processing && <ActivityIndicator size="large" color="#0000ff" style={styles.spinner} />}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  message: {
    fontSize: 18,
    marginBottom: 20,
  },
  spinner: {
    marginTop: 20,
  },
});

export default ProcessVideos;