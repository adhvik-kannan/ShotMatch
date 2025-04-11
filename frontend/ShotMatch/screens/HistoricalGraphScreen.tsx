import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import HistoricalGraph from '@/components/HistoricalGraph';
import MinimalTest from '@/components/TestComponent';
interface Props {
    navigation: NavigationProp<any>;
}

const HistoricalGraphScreen: React.FC<Props> = ({ navigation }) => {
    return <HistoricalGraph navigation={navigation} />;
};

export default HistoricalGraphScreen;