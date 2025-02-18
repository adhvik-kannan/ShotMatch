import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import ProcessVideos from '@/components/ProcessVideos';
interface Props {
    navigation: NavigationProp<any>;
}

const ProcessVideosScreen: React.FC<Props> = ({ navigation }) => {
    return <ProcessVideos navigation={navigation} />;
};

export default ProcessVideosScreen;