import React from 'react';
import Home from '../components/Home';
import { NavigationProp } from '@react-navigation/native';

interface Props {
    navigation: NavigationProp<any>;
}

const HomeScreen: React.FC<Props> = ({ navigation }) => {
    return <Home navigation={navigation} />;
};

export default HomeScreen;