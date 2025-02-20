import React from 'react';
import { View, Text, ScrollView, StyleSheet, Button } from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';
import Svg, { Circle, Text as SvgText } from 'react-native-svg';

type Metric = {
  metric: string;
  you: number;
  player: number;
};

type RootStackParamList = {
  PerformanceMetrics: { metrics: Metric[]; selectedPlayer: { name: string; image: string } };
};

type PerformanceMetricsRouteProp = RouteProp<RootStackParamList, 'PerformanceMetrics'>;

interface HomeProps {
  navigation: any;
}

const PerformanceMetrics: React.FC<HomeProps> = ({ navigation }) => {
  const route = useRoute<PerformanceMetricsRouteProp>();
  const { metrics, selectedPlayer } = route.params;

  // For demonstration, use a dummy similarity score. Replace with your computed value if needed.
  const similarityScore = 50;
  const radius = 45;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - similarityScore / 100);

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer} horizontal={false}>
      <View style={styles.container}>
        <View style={styles.similarityContainer}>
          <Svg height="100" width="100" viewBox="0 0 100 100">
            {/* Background Circle (red) */}
            <Circle
              cx="50"
              cy="50"
              r={radius}
              stroke="red"
              strokeWidth={strokeWidth}
              fill="none"
            />
            {/* Progress Circle (green) */}
            <Circle
              cx="50"
              cy="50"
              r={radius}
              stroke="green"
              strokeWidth={strokeWidth}
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              rotation="-90"
              origin="50,50"
            />
            {/* Similarity Score as Text */}
            <SvgText x="50" y="55" fontSize="18" fill="black" textAnchor="middle">
              {`${similarityScore}%`}
            </SvgText>
          </Svg>
        </View>
        <View style={styles.table}>
          <View style={styles.headerRow}>
            <Text style={[styles.headerCell, styles.youColumn]}>Your Metrics</Text>
            <Text style={[styles.headerCell, styles.metricColumn]}>Metric</Text>
            <Text style={[styles.headerCell, styles.playerColumn]}>{selectedPlayer.name}</Text>
          </View>
          {metrics.map((item, index) => (
            <View key={index} style={styles.row}>
              <Text style={[styles.cell, styles.youColumn]}>{item.you}</Text>
              <Text style={[styles.cell, styles.metricColumn]}>{item.metric}</Text>
              <Text style={[styles.cell, styles.playerColumn]}>{item.player}</Text>
            </View>
          ))}
        </View>
        {/* Buttons at the bottom */}
        <View style={styles.buttonContainer}>
          <Button title="Home" onPress={() => navigation.navigate('Home')} />
          <Button title="Switch Players" onPress={() => navigation.navigate('Compare')} />
          <Button title="Upload More Videos" onPress={() => navigation.navigate('UploadVideos', { selectedPlayer: selectedPlayer })} />
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollContainer: {
    padding: 20,
  },
  container: {
    flexDirection: 'column',
    minWidth: 400,
  },
  similarityContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  table: {
    flexDirection: 'column',
    marginBottom: 20,
  },
  headerRow: {
    flexDirection: 'row',
    backgroundColor: '#EEE',
    paddingVertical: 10,
  },
  row: {
    flexDirection: 'row',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#CCC',
  },
  headerCell: {
    fontWeight: 'bold',
    textAlign: 'center',
    flex: 1,
  },
  cell: {
    textAlign: 'center',
    flex: 1,
  },
  youColumn: {
    flex: 1,
  },
  metricColumn: {
    flex: 1,
  },
  playerColumn: {
    flex: 1,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 20,
  },
});

export default PerformanceMetrics;