import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import Compare
 from '@/components/Compare';
interface Props {
    navigation: NavigationProp<any>;
}

const CompareScreen: React.FC<Props> = ({ navigation }) => {
    return <Compare navigation={navigation} />;
};

export default CompareScreen;