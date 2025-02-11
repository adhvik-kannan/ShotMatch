import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { NavigationProp } from '@react-navigation/native';

interface Props {
    navigation: NavigationProp<any>;
}

const CreateAccount: React.FC<Props> = ({ navigation }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleCreateAccount = async () => {
        try {
            const response = await fetch('http://128.46.4.97:5000/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await response.json();
            if (response.ok) {
                // Handle successful account creation (e.g., navigate to login)
                Alert.alert('Success', 'Account created successfully');
                navigation.navigate('Login');
            } else {
                Alert.alert('Error', data.message || 'Account creation failed');
            }
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'An error occurred while creating your account.');
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Create Account</Text>
            <TextInput
                style={styles.input}
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
            />
            <TextInput
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
            />
            <Button title="Create Account" onPress={handleCreateAccount} />
            <Button title="Back to Login" onPress={() => navigation.navigate('Login')} />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        padding: 16,
    },
    title: {
        fontSize: 24,
        marginBottom: 16,
        textAlign: 'center',
    },
    input: {
        height: 40,
        borderColor: 'gray',
        borderWidth: 1,
        marginBottom: 12,
        paddingHorizontal: 8,
    },
});

export default CreateAccount;