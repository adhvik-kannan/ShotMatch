import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import ConsistencyResults from '@/components/ConsistencyResults';
interface Props {
    navigation: NavigationProp<any>;
}

const ConsistencyResultsScreen: React.FC<Props> = ({ navigation }) => {
    return <ConsistencyResults navigation={navigation} />;
};

export default ConsistencyResultsScreen;