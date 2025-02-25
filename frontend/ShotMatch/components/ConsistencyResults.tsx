import React from 'react';
import { View, Text, ScrollView, StyleSheet, Button } from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';

type Metric = {
  metric: string;
  score: number;
};

type RootStackParamList = {
  ConsistencyResults: { 
    frontData: Metric[];
    sideData: Metric[];
    overallScore: number;
  };
};

type ConsistencyResultsRouteProp = RouteProp<RootStackParamList, 'ConsistencyResults'>;

interface ResultsProps {
  navigation: any;
}

const ConsistencyResults: React.FC<ResultsProps> = ({ navigation }) => {
  const route = useRoute<ConsistencyResultsRouteProp>();
  const { frontData, sideData, overallScore } = route.params;

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Consistency Results</Text>

      <View style={styles.overallScoreContainer}>
        <Text style={styles.overallScoreText}>Overall Score: {overallScore}%</Text>
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
        <Button title="Home" onPress={() => navigation.navigate('Home')} />
        <Button title="Upload More Videos" onPress={() => navigation.navigate('Consistency')} />
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
    fontWeight: '600'
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