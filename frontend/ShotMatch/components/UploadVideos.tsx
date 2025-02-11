import React, { useState, useEffect } from 'react';
import { View, Button, Text, StyleSheet, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
interface HomeProps {
    navigation: any;
}
const UploadVideos: React.FC<HomeProps> = ({ navigation }) => {
    const [video, setVideo] = useState<string | null>(null);
    const [permissionGranted, setPermissionGranted] = useState<boolean>(false);

    useEffect(() => {
        (async () => {
            if (Platform.OS !== 'web') {
                const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
                setPermissionGranted(status === 'granted');
            }
        })();
    }, []);

    const pickVideo = async () => {
        if (!permissionGranted) {
            alert('Permission to access media library is required!');
            return;
        }
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Videos,
            allowsEditing: false,
            quality: 1,
        });
        if (!result.canceled) {
            if (result.assets && result.assets.length > 0) {
                setVideo(result.assets[0].uri);
            }
        }
    };

    return (
        <View style={styles.container}>
            <Button title="Select Video" onPress={pickVideo} />
            {video && <Text style={styles.videoText}>Selected Video: {video}</Text>}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    videoText: {
        marginTop: 20,
        fontSize: 16,
    },
});

export default UploadVideos;