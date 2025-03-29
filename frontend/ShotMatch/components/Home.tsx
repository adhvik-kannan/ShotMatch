import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';

interface HomeProps {
    navigation: any;
}

// type UserData = {
//   email: string;
// };

type RootStackParamList = {
    User: { user: string };
};

type ProcessVideosRouteProp = RouteProp<RootStackParamList, 'User'>;

const Home: React.FC<HomeProps> = ({ navigation }) => {
    const route = useRoute<ProcessVideosRouteProp>();
    const { user } = route.params;

    return (
        <View style={styles.container}>
            <TouchableOpacity 
                style={styles.button} 
                onPress={() => navigation.navigate('Compare', { user: user })}
            >
                <Text style={styles.buttonText}>Compare With an NBA Player</Text>
            </TouchableOpacity>
            <TouchableOpacity 
                style={styles.button} 
                onPress={() => navigation.navigate('Consistency', { user: user })}
            >
                <Text style={styles.buttonText}>Consistency: Compare With Yourself</Text>
            </TouchableOpacity>
            <TouchableOpacity 
                style={styles.button} 
                onPress={() => navigation.navigate('HistoricalGraph', { user: user })}
            >
                <Text style={styles.buttonText}>Historical Graph</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 20,
    },
    button: {
        flex: 1,
        backgroundColor: '#007AFF',
        marginVertical: 10,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 8,
        padding: 20,
    },
    buttonText: {
        color: '#FFFFFF',
        fontSize: 18,
        fontWeight: '600',
    },
});

export default Home;