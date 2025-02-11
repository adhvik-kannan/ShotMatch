import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/LoginScreen';
import CreateAccountScreen from '../screens/CreateAccountScreen';
import HomeScreen from '../screens/HomeScreen';
import ConsistencyScreen from '../screens/ConsistencyScreen';
import UploadVideosScreen from '../screens/UploadVideosScreen';
const Stack = createStackNavigator();

const AuthNavigator = () => {
    return (
        <Stack.Navigator initialRouteName="Login">
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="CreateAccount" component={CreateAccountScreen} />
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Consistency" component={ConsistencyScreen} />
            <Stack.Screen name="UploadVideos" component={UploadVideosScreen} />
        </Stack.Navigator>
    );
};

export default AuthNavigator;