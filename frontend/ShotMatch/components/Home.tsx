import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface HomeProps {
    navigation: any;
}

const Home: React.FC<HomeProps> = ({ navigation }) => {
    return (
        <View style={styles.container}>
            <TouchableOpacity 
                style={styles.button} 
                onPress={() => navigation.navigate('Consistency')}
            >
                <Text style={styles.buttonText}>Compare With an NBA Player</Text>
            </TouchableOpacity>
            <TouchableOpacity 
                style={styles.button} 
                onPress={() => console.log('Consistency: Compare With Yourself pressed')}
            >
                <Text style={styles.buttonText}>Consistency: Compare With Yourself</Text>
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