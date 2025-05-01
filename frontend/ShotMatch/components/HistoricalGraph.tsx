import React, { useCallback, useState, useEffect, useMemo } from 'react';
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
  // In Compare mode you might have nested objects,
  // but in Consistency mode these keys are directly stored as numbers.
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

// Mapping objects for Consistency mode display names.
const consistencyMappingFront: { [key: string]: string } = {
  "max_front_results": "Release Score",
  "eye_front_results": "Eye Level Score",
  "waist_front_results": "Waist Score"
};
const consistencyMappingSide: { [key: string]: string } = {
  "max_side_results": "Release Score",
  "eye_side_results": "Eye Level Score",
  "waist_side_results": "Waist Score"
};

const HistoricalGraph: React.FC<HomeProps> = ({ navigation }) => {
  const isFocused = useIsFocused();
  const route = useRoute<HistoricalGraphRouteProp>();
  const { user } = route.params;
  const [playerData, setPlayerData] = useState<PlayerData[]>([]);
  const [section, setSection] = useState<'front' | 'side' | 'overall'>('front');
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [mode, setMode] = useState<'Compare' | 'Consistency'>('Compare');

  // Time Range State
  const [timeRange, setTimeRange] = useState<string>('2 Days');
  const timeRangeOptions = ['1 Day', '2 Days', '1 Week', '1 Month'];

  // Group selection only applies in Compare mode.
  const groups = ['max', 'eye', 'waist'];
  const [selectedGroup, setSelectedGroup] = useState<string>('max');

  const [selectedPoint, setSelectedPoint] = useState<SelectedPoint | null>(null);

  // Fetch data on focus.
  useFocusEffect(
    useCallback(() => {
      const backendUrl: string = Constants.expoConfig?.extra?.backendUrl;
      const backendPort: string = Constants.expoConfig?.extra?.backendPort;
      const fetchData = async () => {
        try {
          const response = await fetch(`http://${backendUrl}:${backendPort}/player_data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user })
          });
          const json = await response.json();
          const data: PlayerData[] = json.player_data || [];
          setPlayerData(data);
          if (data.length > 0) {
            if (data[0].mode === "Compare") {
              // For Compare mode, use dynamic keys from front_results.
              const frontKeys = data[0]?.front_results ? Object.keys(data[0].front_results) : [];
              setSection('front');
              setCategories(frontKeys);
              if (frontKeys.length > 0) setSelectedCategory(frontKeys[0]);
            } else {
              // In Consistency mode, set default categories for front.
              setSection('front');
              const consFront = ["max_front_results", "eye_front_results", "waist_front_results"];
              setCategories(consFront);
              setSelectedCategory(consFront[0]);
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

  // Helper: extract a Date from the record.
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

  // Compute validData using useMemo.
  const validData = useMemo(() => {
    const modeData = playerData.filter(item => item.mode === mode);
    return modeData
      .filter(item => getRecordDate(item) !== null)
      .sort((a, b) => {
        const dateA = getRecordDate(a);
        const dateB = getRecordDate(b);
        if (!dateA || !dateB) return 0;
        return dateA.getTime() - dateB.getTime();
      });
  }, [playerData, mode]);

  // Format helpers.
  const formatShortDate = (date: Date) => {
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${monthNames[date.getMonth()]} ${date.getDate()}`;
  };

  const formatFullDateTime = (date: Date) => {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
  };

  let chartLabels: string[] = [];
  let chartDataPoints: number[] = [];
  let chartDates: Date[] = [];

  // Build chart data based on time range.
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
            ? (mode === 'Consistency'
                ? Number(item[selectedCategory])
                : Number(item[`${selectedGroup}_front_results`]?.[selectedCategory]))
            : (mode === 'Consistency'
                ? Number(item[selectedCategory])
                : Number(item[`${selectedGroup}_side_results`]?.[selectedCategory]));
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
      return (index % step === 0 || index === total - 1) ? formatShortDate(item.date) : "";
    });
    const refMonth = referenceDate.getMonth();
    for (let i = 0; i < dailyArray.length - 1; i++) {
      const currentMonth = dailyArray[i].date.getMonth();
      const nextMonth = dailyArray[i + 1].date.getMonth();
      if (currentMonth !== refMonth && nextMonth === refMonth) {
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
    // console.log('recentData:', recentData);
    chartDataPoints = recentData.map(item => {
      let value = 0;
      if (section === 'overall') {
        value = Number(item.overall_score);
      } else if (mode === 'Consistency') {
        // In Consistency mode, data is stored directly as numbers under the key.
        // For front or side, simply use the selectedCategory key.
        if (section === 'front' || section === 'side') {
          value = Number(item[selectedCategory]);
        }
      } else {
        // Compare mode: use the selectedGroup to look up nested data.
        if (section === 'front') {
          value = Number(item[`${selectedGroup}_front_results`]?.[selectedCategory]);
        } else if (section === 'side') {
          value = Number(item[`${selectedGroup}_side_results`]?.[selectedCategory]);
        }
      }
      return isNaN(value) ? 0 : value;
    });
    chartDates = recentData.map(item => getRecordDate(item) || new Date());
    // if (timeRange === '1 Day' || timeRange === '2 Days') {
    //   const distinctDays: string[] = [];
    //   chartDates.forEach(date => {
    //     const dayStr = `${date.getMonth() + 1}/${date.getDate()}`;
    //     if (!distinctDays.includes(dayStr)) {
    //       distinctDays.push(dayStr);
    //     }
    //   });
    //   const lastTwoDays = new Set(distinctDays.slice(-2));
    //   const labeledDays = new Set<string>();
    //   chartLabels = chartDates.map(date => {
    //     const dayStr = `${date.getMonth() + 1}/${date.getDate()}`;
    //     const timeLabel = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
    //     if (lastTwoDays.has(dayStr) && !labeledDays.has(dayStr)) {
    //       labeledDays.add(dayStr);
    //       return `${dayStr} ${timeLabel}`;
    //     }
    //     return timeLabel;
    //   });
    if (timeRange === '1 Day' || timeRange === '2 Days') {
      const total = chartDates.length;
      if (total === 0) {
        chartLabels = [];
      } else {
        // Compute 4 predetermined indices: first, one‑third, two‑thirds, and last.
        const predIndices: number[] = [];
        predIndices.push(0);
        if (total > 3) {
          predIndices.push(Math.floor(total / 3));
          predIndices.push(Math.floor((2 * total) / 3));
        }
        if (!predIndices.includes(total - 1)) {
          predIndices.push(total - 1);
        }
        predIndices.sort((a, b) => a - b);
    
        // Build labels array (default blank).
        const labels = Array(total).fill("");
    
        // For the first predetermined index always show full date and time.
        const firstDate = chartDates[predIndices[0]];
        labels[predIndices[0]] = `${firstDate.getMonth() + 1}/${firstDate.getDate()} ${firstDate.getHours()}:${String(firstDate.getMinutes()).padStart(2, '0')}`;

        // For later indices:
        for (let i = 1; i < predIndices.length; i++) {
          const idx = predIndices[i];
          const date = chartDates[idx];
          if (timeRange === '2 Days') {
            // Compare the current label's date with the previous predetermined label's date.
            const prevDate = chartDates[predIndices[i - 1]];
            if (
              date.getDate() !== prevDate.getDate() ||
              date.getMonth() !== prevDate.getMonth() ||
              date.getFullYear() !== prevDate.getFullYear()
            ) {
              // If the day is different, display full date and time.
              labels[idx] = `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
            } else {
              // Otherwise, display the time.
              labels[idx] = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
            }
          } else { // '1 Day' branch always shows time (after the first label).
            labels[idx] = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
          }
        }
        chartLabels = labels;
      }
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

  // Update available categories when section, validData, or mode changes.
  useEffect(() => {
    if (validData.length > 0) {
      if (mode === 'Consistency') {
        // In Consistency mode, we no longer use group selection.
        if (section === 'overall') {
          setCategories(['Overall Score']);
          setSelectedCategory('Overall Score');
        } else if (section === 'front') {
          // Set the keys as stored in your consistency data.
          const consFront = ["max_front_results", "eye_front_results", "waist_front_results"];
          setCategories(consFront);
          setSelectedCategory(consFront[0]);
        } else if (section === 'side') {
          const consSide = ["max_side_results", "eye_side_results", "waist_side_results"];
          setCategories(consSide);
          setSelectedCategory(consSide[0]);
        }
      } else {
        // In Compare mode, use the dynamic group approach.
        if (section === 'overall') {
          setCategories(['overall_score']);
          setSelectedCategory('overall_score');
        } else if (section === 'front') {
          const groupProp = `${selectedGroup}_front_results`;
          const frontKeys = validData[0]?.[groupProp] ? Object.keys(validData[0][groupProp]) : [];
          setCategories(frontKeys);
          if (frontKeys.length > 0) setSelectedCategory(frontKeys[0]);
        } else if (section === 'side') {
          const groupProp = `${selectedGroup}_side_results`;
          const sideKeys = validData[0]?.[groupProp] ? Object.keys(validData[0][groupProp]) : [];
          setCategories(sideKeys);
          if (sideKeys.length > 0) setSelectedCategory(sideKeys[0]);
        }
      }
    }
  }, [section, validData, selectedGroup, mode]);

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
              onPress={() => setSection('front')}
              color={section === 'front' ? '#007AFF' : '#8e8e93'}
            />
            <Button
              title="Side Results"
              onPress={() => setSection('side')}
              color={section === 'side' ? '#007AFF' : '#8e8e93'}
            />
            <Button
              title="Overall Score"
              onPress={() => setSection('overall')}
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
          {/* Only show group picker in Compare mode */}
          {mode === 'Compare' && (section === 'front' || section === 'side') && (
            <View style={styles.pickerContainer}>
              <Text style={styles.subheader}>Select Group:</Text>
              <Picker
                selectedValue={selectedGroup}
                style={styles.picker}
                onValueChange={(itemValue) => setSelectedGroup(itemValue)}
              >
                {groups.map(group => (
                  <Picker.Item key={group} label={group.toUpperCase()} value={group} />
                ))}
              </Picker>
            </View>
          )}
          <View style={styles.pickerContainer}>
            <Text style={styles.subheader}>Select Category:</Text>
            <Picker
              selectedValue={selectedCategory}
              style={styles.picker}
              onValueChange={(itemValue) => setSelectedCategory(itemValue)}
            >
              {categories.map(category => {
                let label = category;
                if (mode === 'Consistency' && section !== 'overall') {
                  // Use friendly display names from the mapping objects.
                  label = section === 'front'
                    ? (consistencyMappingFront[category] || category)
                    : (consistencyMappingSide[category] || category);
                }
                return <Picker.Item key={category} label={label} value={category} />;
              })}
            </Picker>
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
                    <Text style={styles.modalText}>
                      Date: {formatFullDateTime(selectedPoint.date)}
                    </Text>
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
  container: { padding: 10, alignItems: 'center' },
  header: { fontSize: 24, fontWeight: '700', marginBottom: 10 },
  sectionToggle: { flexDirection: 'row', justifyContent: 'space-around', width: '100%', marginVertical: 10 },
  pickerContainer: { width: '90%', marginVertical: 10 },
  subheader: { fontSize: 16, fontWeight: '600', marginBottom: 5 },
  picker: { height: 50, width: '100%' },
  chartContainer: { marginTop: 10, borderWidth: 1, borderColor: '#ccc', borderRadius: 16, overflow: 'hidden' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: '#fff', padding: 20, borderRadius: 10, width: '80%', alignItems: 'center' },
  modalText: { fontSize: 16, marginVertical: 5 },
  closeButton: { marginTop: 15, backgroundColor: '#007AFF', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 5 },
  closeButtonText: { color: '#fff', fontWeight: '600' }
});

export default HistoricalGraph;