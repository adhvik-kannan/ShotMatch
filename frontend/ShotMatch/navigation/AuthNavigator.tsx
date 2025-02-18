import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/LoginScreen';
import CreateAccountScreen from '../screens/CreateAccountScreen';
import HomeScreen from '../screens/HomeScreen';
import CompareScreen from '@/screens/CompareScreen';
import UploadVideosScreen from '../screens/UploadVideosScreen';
import ProcessVideosScreen from '@/screens/ProcessVideosScreen';
const Stack = createStackNavigator();

const AuthNavigator = () => {
    return (
        <Stack.Navigator initialRouteName="Login">
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="CreateAccount" component={CreateAccountScreen} />
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Compare" component={CompareScreen} />
            <Stack.Screen name="UploadVideos" component={UploadVideosScreen} />
            <Stack.Screen name="ProcessVideos" component={ProcessVideosScreen} />
        </Stack.Navigator>
    );
};

export default AuthNavigator;