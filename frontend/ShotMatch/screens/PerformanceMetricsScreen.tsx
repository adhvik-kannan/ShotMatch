import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import PerformanceMetrics from '@/components/PerformanceMetrics';
interface Props {
    navigation: NavigationProp<any>;
}

const PerformanceMetricsScreen: React.FC<Props> = ({ navigation }) => {
    return <PerformanceMetrics navigation={navigation} />;
};

export default PerformanceMetricsScreen;