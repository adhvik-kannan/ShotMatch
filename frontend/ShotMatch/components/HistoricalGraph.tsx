import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
  Button,
  ScrollView,
  Modal,
  TouchableOpacity
} from 'react-native';
import { useRoute, RouteProp, useFocusEffect, useIsFocused } from '@react-navigation/native';
import { LineChart } from 'react-native-chart-kit';
import { Picker } from '@react-native-picker/picker';
import Constants from 'expo-constants';

interface HomeProps {
  navigation: any;
}

type RootStackParamList = {
  HistoricalGraph: { user: string };
};

type HistoricalGraphRouteProp = RouteProp<RootStackParamList, 'HistoricalGraph'>;

interface Timestamp {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
}

interface PlayerData {
  date?: string | {
    day: number;
    month: number;
    year: number;
    hour: number;
    minute: number;
    second: number;
  };
  front_results?: { [key: string]: number };
  side_results?: { [key: string]: number };
  overall_score?: number;
  name?: string;
  mode?: string;
  timestamp?: Timestamp;
}

interface SelectedPoint {
  date: Date;
  value: number;
}

const HistoricalGraph: React.FC<HomeProps> = ({ navigation }) => {
  const isFocused = useIsFocused();
  console.log('isFocused:', isFocused);
  const route = useRoute<HistoricalGraphRouteProp>();
  const { user } = route.params;
  const [playerData, setPlayerData] = useState<PlayerData[]>([]);
  const [section, setSection] = useState<'front' | 'side' | 'overall'>('front');
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Only these time range options are allowed.
  const [timeRange, setTimeRange] = useState<string>('2 Days');
  const timeRangeOptions = ['1 Day', '2 Days', '1 Week', '1 Month'];

  // State for the selected data point pop out.
  const [selectedPoint, setSelectedPoint] = useState<SelectedPoint | null>(null);
  // Mode toggle state.
  const [mode, setMode] = useState<'Compare' | 'Consistency'>('Compare');

  useFocusEffect(
    useCallback(() => {
      const backendUrl: string = Constants.expoConfig?.extra?.backendUrl;
      const backendPort: string = Constants.expoConfig?.extra?.backendPort;
      console.log("Backend URL:", backendUrl);
      const fetchData = async () => {
        console.log('Fetching data for user:', user);
        try {
          // Note: We now only send the user so all records (for both modes) are returned.
          const response = await fetch(`http://${backendUrl}:${backendPort}/player_data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user })
          });
          const json = await response.json();
          const data: PlayerData[] = json.player_data || [];
          setPlayerData(data);
          if (data.length > 0) {
            // Initialize with the default mode's (Compare) data.
            const compareData = data.filter(item => item.mode === "Compare");
            const frontKeys = compareData[0]?.front_results ? Object.keys(compareData[0].front_results) : [];
            setSection('front');
            setCategories(frontKeys);
            if (frontKeys.length > 0) {
              setSelectedCategory(frontKeys[0]);
            }
          }
        } catch (error) {
          console.error('Error fetching player data:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }, [user])
  );

  // Helper: extract a valid Date from a record.
  const getRecordDate = (item: PlayerData): Date | null => {
    if (item.date) {
      if (typeof item.date === 'string') {
        const d = new Date(item.date);
        return isNaN(d.getTime()) ? null : d;
      } else if (typeof item.date === 'object') {
        const { day, month, year, hour, minute, second } = item.date as any;
        const d = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second));
        return isNaN(d.getTime()) ? null : d;
      }
    } else if (item.timestamp) {
      const { year, month, day, hour, minute, second } = item.timestamp;
      const d = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second));
      return isNaN(d.getTime()) ? null : d;
    }
    return null;
  };

  // console.log('playerData:', playerData);
  // Filter records by mode locally.
  const modeData = playerData.filter(item => item.mode === mode);
  
  // Validate and sort data chronologically.
  const validData = modeData
    .filter(item => getRecordDate(item) !== null)
    .sort((a, b) => {
      const dateA = getRecordDate(a);
      const dateB = getRecordDate(b);
      if (!dateA || !dateB) return 0;
      return dateA.getTime() - dateB.getTime();
    });

  let chartLabels: string[] = [];
  let chartDataPoints: number[] = [];
  let chartDates: Date[] = [];

  // Helper: format a date as "Mar 28"
  const formatShortDate = (date: Date) => {
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${monthNames[date.getMonth()]} ${date.getDate()}`;
  };

  // Helper: format full date/time for the modal.
  const formatFullDateTime = (date: Date) => {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
  };

  if (timeRange === '1 Month') {
    const referenceDate =
      validData.length > 0 ? getRecordDate(validData[validData.length - 1]) || new Date() : new Date();
    const cutoffDate = new Date(referenceDate.getTime() - 30 * 24 * 60 * 60 * 1000);
    const monthData = validData.filter(item => {
      const d = getRecordDate(item);
      return d && d >= cutoffDate;
    });
    const dailyMap = new Map<string, { date: Date, value: number }>();
    monthData.forEach(item => {
      const d = getRecordDate(item);
      if (d) {
        const value = section === 'overall'
          ? Number(item.overall_score)
          : section === 'front'
            ? Number(item.front_results?.[selectedCategory])
            : Number(item.side_results?.[selectedCategory]);
        const key = d.toDateString();
        if (!dailyMap.has(key) || value > (dailyMap.get(key)?.value ?? 0)) {
          dailyMap.set(key, { date: d, value });
        }
      }
    });
    const dailyArray = Array.from(dailyMap.values()).sort((a, b) => a.date.getTime() - b.date.getTime());
    chartDataPoints = dailyArray.map(item => item.value);
    chartDates = dailyArray.map(item => item.date);
    const total = dailyArray.length;
    const desiredLabelsCount = 4;
    const step = Math.max(1, Math.floor(total / desiredLabelsCount));
    chartLabels = dailyArray.map((item, index) => {
      if (index % step === 0 || index === total - 1) {
        return formatShortDate(item.date);
      }
      return "";
    });
    const referenceMonth = referenceDate.getMonth();
    for (let i = 0; i < dailyArray.length - 1; i++) {
      const currentMonth = dailyArray[i].date.getMonth();
      const nextMonth = dailyArray[i + 1].date.getMonth();
      if (currentMonth !== referenceMonth && nextMonth === referenceMonth) {
        chartLabels[i] = "";
      }
    }
  } else {
    let days = 2;
    if (timeRange === '1 Day') days = 1;
    else if (timeRange === '1 Week') days = 7;
    const referenceDate =
      validData.length > 0 ? getRecordDate(validData[validData.length - 1]) || new Date() : new Date();
    const cutoffDate = new Date(referenceDate.getTime() - days * 24 * 60 * 60 * 1000);
    const recentData = validData.filter(item => {
      const d = getRecordDate(item);
      return d && d >= cutoffDate;
    });
    chartDataPoints = recentData.map(item =>
      section === 'overall'
        ? Number(item.overall_score)
        : section === 'front'
          ? Number(item.front_results?.[selectedCategory])
          : Number(item.side_results?.[selectedCategory])
    );
    chartDates = recentData.map(item => getRecordDate(item) || new Date());
    if (timeRange === '1 Day' || timeRange === '2 Days') {
      const distinctDays: string[] = [];
      chartDates.forEach(date => {
        const dayStr = `${date.getMonth() + 1}/${date.getDate()}`;
        if (!distinctDays.includes(dayStr)) {
          distinctDays.push(dayStr);
        }
      });
      const lastTwoDays = new Set(distinctDays.slice(-2));
      const labeledDays = new Set<string>();
      chartLabels = chartDates.map(date => {
        const dayStr = `${date.getMonth() + 1}/${date.getDate()}`;
        const timeLabel = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
        if (lastTwoDays.has(dayStr) && !labeledDays.has(dayStr)) {
          labeledDays.add(dayStr);
          return `${dayStr} ${timeLabel}`;
        }
        return timeLabel;
      });
    } else if (timeRange === '1 Week') {
      const total = chartDates.length;
      const desiredLabelsCount = 4;
      const step = Math.max(1, Math.floor(total / desiredLabelsCount));
      let lastLabel = "";
      chartLabels = [];
      for (let i = 0; i < total; i++) {
        if (i % step === 0 || i === total - 1) {
          const label = formatShortDate(chartDates[i]);
          if (label === lastLabel) {
            chartLabels.push("");
          } else {
            chartLabels.push(label);
            lastLabel = label;
          }
        } else {
          chartLabels.push("");
        }
      }
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : (
        <>
          <Text style={styles.header}>Historical Graph</Text>
          <View style={styles.sectionToggle}>
            <Button
              title="Front Results"
              onPress={() => {
                setSection('front');
                const frontKeys = validData[0]?.front_results ? Object.keys(validData[0].front_results) : [];
                setCategories(frontKeys);
                if (frontKeys.length > 0) setSelectedCategory(frontKeys[0]);
              }}
              color={section === 'front' ? '#007AFF' : '#8e8e93'}
            />
            <Button
              title="Side Results"
              onPress={() => {
                setSection('side');
                const sideKeys = validData[0]?.side_results ? Object.keys(validData[0].side_results) : [];
                setCategories(sideKeys);
                if (sideKeys.length > 0) setSelectedCategory(sideKeys[0]);
              }}
              color={section === 'side' ? '#007AFF' : '#8e8e93'}
            />
            <Button
              title="Overall Score"
              onPress={() => {
                setSection('overall');
                setCategories(['overall_score']);
                setSelectedCategory('overall_score');
              }}
              color={section === 'overall' ? '#007AFF' : '#8e8e93'}
            />
          </View>
          <View style={styles.sectionToggle}>
            <Button
              title="Compare"
              onPress={() => setMode('Compare')}
              color={mode === 'Compare' ? '#007AFF' : '#8e8e93'}
            />
            <Button
              title="Consistency"
              onPress={() => setMode('Consistency')}
              color={mode === 'Consistency' ? '#007AFF' : '#8e8e93'}
            />
          </View>
          <View style={styles.pickerContainer}>
            <Text style={styles.subheader}>Select Time Range:</Text>
            <Picker
              selectedValue={timeRange}
              style={styles.picker}
              onValueChange={(itemValue) => setTimeRange(itemValue)}
            >
              {timeRangeOptions.map(option => (
                <Picker.Item key={option} label={option} value={option} />
              ))}
            </Picker>
          </View>
          <View style={styles.pickerContainer}>
            <Text style={styles.subheader}>Select Category:</Text>
            <Picker
              selectedValue={selectedCategory}
              style={styles.picker}
              onValueChange={(itemValue) => setSelectedCategory(itemValue)}
            >
              {categories.map(category => (
                <Picker.Item key={category} label={category} value={category} />
              ))}
            </Picker>
          </View>
          <View style={styles.chartContainer}>
            {chartDataPoints.length > 0 ? (
              <LineChart
                data={{
                  labels: chartLabels,
                  datasets: [{ data: chartDataPoints }]
                }}
                width={Dimensions.get('window').width - 20}
                height={220}
                chartConfig={{
                  backgroundColor: "#ffffff",
                  backgroundGradientFrom: "#ffffff",
                  backgroundGradientTo: "#ffffff",
                  decimalPlaces: 2,
                  color: (opacity = 1) => `rgba(0, 0, 255, ${opacity})`,
                  labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                  style: { borderRadius: 16 },
                  propsForDots: {
                    r: "4",
                    strokeWidth: "2",
                    stroke: "#0000ff"
                  }
                }}
                bezier
                style={{
                  marginVertical: 8,
                  borderRadius: 16
                }}
                onDataPointClick={({ value, index }) => {
                  setSelectedPoint({ date: chartDates[index], value: Number(value) });
                }}
                withVerticalLabels
              />
            ) : (
              <Text>No data available.</Text>
            )}
          </View>
          <Modal
            visible={selectedPoint !== null}
            transparent
            animationType="fade"
            onRequestClose={() => setSelectedPoint(null)}
          >
            <View style={styles.modalOverlay}>
              <View style={styles.modalContent}>
                {selectedPoint && (
                  <>
                    <Text style={styles.modalText}>Date: {formatFullDateTime(selectedPoint.date)}</Text>
                    <Text style={styles.modalText}>Value: {selectedPoint.value}</Text>
                  </>
                )}
                <TouchableOpacity style={styles.closeButton} onPress={() => setSelectedPoint(null)}>
                  <Text style={styles.closeButtonText}>Close</Text>
                </TouchableOpacity>
              </View>
            </View>
          </Modal>
        </>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
    alignItems: 'center'
  },
  header: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 10
  },
  sectionToggle: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginVertical: 10
  },
  pickerContainer: {
    width: '90%',
    marginVertical: 10
  },
  subheader: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5
  },
  picker: {
    height: 50,
    width: '100%'
  },
  chartContainer: {
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 16,
    overflow: 'hidden'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    width: '80%',
    alignItems: 'center'
  },
  modalText: {
    fontSize: 16,
    marginVertical: 5
  },
  closeButton: {
    marginTop: 15,
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5
  },
  closeButtonText: {
    color: '#fff',
    fontWeight: '600'
  }
});

export default HistoricalGraph;