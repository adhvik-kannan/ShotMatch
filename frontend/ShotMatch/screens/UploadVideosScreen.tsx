import React from 'react';
import { NavigationProp } from '@react-navigation/native';
import UploadVideos from '@/components/UploadVideos';
interface Props {
    navigation: NavigationProp<any>;
}

const UploadVideosScreen: React.FC<Props> = ({ navigation }) => {
    return <UploadVideos navigation={navigation} />;
};

export default UploadVideosScreen;