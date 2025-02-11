import { registerRootComponent } from 'expo';
import { Text, View } from "react-native";
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import App from '../App';

// Register only one NavigationContainer at the root
export default function Index() { 
    return <App />;
}
registerRootComponent(Index);