import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import Constants from 'expo-constants';

type VideoData = {
  videoUri: string;
  thumbnailUri: string;
};

type RootStackParamList = {
  ProcessVideos: { videos: VideoData[], selectedPlayer: any };
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
        const response = await fetch(`http://${Constants.expoConfig?.extra.backendUrl}:5000/process_videos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ videos }),
        });
        if (response.ok) {
            const dummyMetrics = [
                { metric: "Points", you: 25, player: 30 },
                { metric: "Assists", you: 7, player: 5 },
                { metric: "Rebounds", you: 10, player: 8 },
                // Add more metric rows as needed
            ];
            setMessage('Videos processed successfully!');
            setTimeout(() => {
                navigation.navigate('PerformanceMetrics', { metrics: dummyMetrics, selectedPlayer });
            }, 1000);
        } else {
          setMessage('Failed to process videos.');
          setTimeout(() => {
            navigation.navigate('UploadVideos');
          }, 1500);
        }
      } catch (error) {
        console.error(error);
        setMessage('Error processing videos.');
        setTimeout(() => {
            navigation.navigate('UploadVideos');
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