import React from 'react';
import { View, Text, ScrollView, StyleSheet, Button } from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';
import Svg, { Circle, Text as SvgText } from 'react-native-svg';

type FrontMetrics = { [key: string]: number };
type SideMetrics = { [key: string]: number };

type RootStackParamList = {
  PerformanceMetrics: { 
    frontMetrics: FrontMetrics;
    sideMetrics: SideMetrics;
    selectedPlayer: { name: string; image: string };
    overallComparisonScore: number;
    user: string;
  }
};

type PerformanceMetricsRouteProp = RouteProp<RootStackParamList, 'PerformanceMetrics'>;

interface HomeProps {
  navigation: any;
}

const PerformanceMetrics: React.FC<HomeProps> = ({ navigation }) => {
  const route = useRoute<PerformanceMetricsRouteProp>();
  const { frontMetrics, sideMetrics, selectedPlayer, overallComparisonScore, user } = route.params;

  // Circle configurations
  const radius = 45;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - overallComparisonScore / 100);
  const roundedOverallScore = Math.round(overallComparisonScore);

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.container}>
        <Text style={styles.title}>Performance Metrics</Text>

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
            {/* Overall Score Text */}
            <SvgText 
              x="50" 
              y="55" 
              fontSize="18" 
              fill="black" 
              textAnchor="middle"
            >
              {`${roundedOverallScore}%`}
            </SvgText>
          </Svg>
        </View>

        <Text style={styles.subTitle}>Front View Metrics</Text>
        <View style={styles.table}>
          <View style={styles.headerRow}>
            <Text style={styles.headerCell}>Metric</Text>
            <Text style={styles.headerCell}>You</Text>
          </View>
          {Object.entries(frontMetrics)
            .filter(([metric]) => metric !== 'sew_la_score')
            .map(([metric, score], index) => (
              <View key={index} style={styles.row}>
                <Text style={styles.cell}>{metric}</Text>
                <Text style={styles.cell}>{score}</Text>
              </View>
          ))}
        </View>

        <Text style={styles.subTitle}>Side View Metrics</Text>
        <View style={styles.table}>
          <View style={styles.headerRow}>
            <Text style={styles.headerCell}>Metric</Text>
            <Text style={styles.headerCell}>You</Text>
          </View>
          {Object.entries(sideMetrics).map(([metric, score], index) => (
            <View key={index} style={styles.row}>
              <Text style={styles.cell}>{metric}</Text>
              <Text style={styles.cell}>{score}</Text>
            </View>
          ))}
        </View>

        <View style={styles.buttonContainer}>
          <Button title="Home" onPress={() => navigation.navigate('Home', { user: user })} />
          <Button title="Switch Players" onPress={() => navigation.navigate('Compare', { user: user })} />
          <Button title="Upload More Videos" onPress={() => navigation.navigate('UploadVideos', { selectedPlayer: selectedPlayer, user: user })} />
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollContainer: {
    padding: 20,
    backgroundColor: '#fff'
  },
  container: {
    flexDirection: 'column',
    minWidth: 400,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20
  },
  similarityContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  subTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 10
  },
  table: {
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#ccc'
  },
  headerRow: {
    flexDirection: 'row',
    backgroundColor: '#eee',
    padding: 10
  },
  headerCell: {
    flex: 1,
    textAlign: 'center',
    fontWeight: 'bold'
  },
  row: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    padding: 10
  },
  cell: {
    flex: 1,
    textAlign: 'center'
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around'
  }
});

export default PerformanceMetrics;