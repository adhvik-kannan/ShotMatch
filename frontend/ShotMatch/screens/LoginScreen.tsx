import React from 'react';
import Login from '../components/Login';
import { NavigationProp } from '@react-navigation/native';

interface Props {
    navigation: NavigationProp<any>;
}

const LoginScreen: React.FC<Props> = ({ navigation }) => {
    return <Login navigation={navigation} />;
};

export default LoginScreen;