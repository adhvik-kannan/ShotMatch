import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import Consistency
 from '@/components/Consistency';
interface Props {
    navigation: NavigationProp<any>;
}

const ConsistencyScreen: React.FC<Props> = ({ navigation }) => {
    return <Consistency navigation={navigation} />;
};

export default ConsistencyScreen;