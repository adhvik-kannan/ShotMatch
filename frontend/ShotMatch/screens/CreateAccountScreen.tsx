import React from 'react';
import CreateAccount from '../components/CreateAccount';
import { NavigationProp } from '@react-navigation/native';

interface Props {
    navigation: NavigationProp<any>;
}

const CreateAccountScreen: React.FC<Props> = ({ navigation }) => {
    return <CreateAccount navigation={navigation} />;
};

export default CreateAccountScreen;