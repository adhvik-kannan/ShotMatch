import React from 'react';
import { View, Text, ScrollView, StyleSheet, Button } from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';
import Svg, { Circle, Text as SvgText } from 'react-native-svg';

type Metric = {
  metric: string;
  score: number;
};

type RootStackParamList = {
  ConsistencyResults: { 
    frontData: Metric[];
    sideData: Metric[];
    overallScore: number;
    user: string;
  };
};

type ConsistencyResultsRouteProp = RouteProp<RootStackParamList, 'ConsistencyResults'>;

interface ResultsProps {
  navigation: any;
}

const ConsistencyResults: React.FC<ResultsProps> = ({ navigation }) => {
  const route = useRoute<ConsistencyResultsRouteProp>();
  const { frontData, sideData, overallScore, user } = route.params;
  
  // Circle configurations identical to PerformanceMetrics.tsx
  const radius = 45;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - overallScore / 100);
  const roundedOverallScore = Math.round(overallScore);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Consistency Results</Text>

      <View style={styles.overallScoreContainer}>
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
        <Text style={styles.overallScoreText}>Overall Score</Text>
      </View>

      <Text style={styles.subTitle}>Front View Results</Text>
      <View style={styles.table}>
        <View style={styles.headerRow}>
          <Text style={styles.headerCell}>Metric</Text>
          <Text style={styles.headerCell}>Score</Text>
        </View>
        {frontData.map((item, index) => (
          <View key={index} style={styles.row}>
            <Text style={styles.cell}>{item.metric}</Text>
            <Text style={styles.cell}>{item.score}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.subTitle}>Side View Results</Text>
      <View style={styles.table}>
        <View style={styles.headerRow}>
          <Text style={styles.headerCell}>Metric</Text>
          <Text style={styles.headerCell}>Score</Text>
        </View>
        {sideData.map((item, index) => (
          <View key={index} style={styles.row}>
            <Text style={styles.cell}>{item.metric}</Text>
            <Text style={styles.cell}>{item.score}</Text>
          </View>
        ))}
      </View>

      <View style={styles.buttonContainer}>
        <Button title="Home" onPress={() => navigation.navigate('Home', { user })} />
        <Button title="Upload More Videos" onPress={() => navigation.navigate('Consistency', { user })} />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20
  },
  overallScoreContainer: {
    alignItems: 'center',
    marginBottom: 20
  },
  overallScoreText: {
    fontSize: 20,
    fontWeight: '600',
    marginTop: 10
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

export default ConsistencyResults;