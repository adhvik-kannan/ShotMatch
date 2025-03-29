import React from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    ImageBackground,
    ScrollView,
    Dimensions,
    StyleSheet,
} from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';

interface HomeProps {
    navigation: any;
}

const playerData = [
    { id: '1', name: 'LeBron James', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/LeBron_James_%2815662939969%29.jpg/220px-LeBron_James_%2815662939969%29.jpg' },
    { id: '2', name: 'Stephen Curry', image: 'https://phantom-marca.unidadeditorial.es/9b640ceb9e0621afd7b170f4713cae15/crop/0x0/1978x1318/resize/828/f/jpg/assets/multimedia/imagenes/2024/08/21/17242700992805.png' },
    { id: '3', name: 'Klay Thompson', image: 'https://www.kxan.com/wp-content/uploads/sites/40/2024/07/66837247e3f139.26670422.jpeg?strip=1' },
];

const screenWidth = Dimensions.get('window').width;
const screenHeight = Dimensions.get('window').height;
const buttonWidth = screenWidth - 40;  // full width with side margins
// Calculate a button height so that (for example) two buttons are fully visible in portrait mode
const buttonHeight = (screenHeight - 40 - 10) / 2; 
// 40 accounts for the container padding and 10 for margin between buttons
type RootStackParamList = {
    User: { user: string };
};

type ProcessVideosRouteProp = RouteProp<RootStackParamList, 'User'>;

const Compare: React.FC<HomeProps> = ({ navigation }) => {
    const route = useRoute<ProcessVideosRouteProp>();
    const { user } = route.params;

    return (
        <View style={styles.container}>
            <ScrollView
                style={styles.scrollContainer}
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
            >
                {playerData.map((player) => (
                    <TouchableOpacity
                        key={player.id}
                        style={styles.playerButton}
                        onPress={() => navigation.navigate('UploadVideos', { selectedPlayer: player, user: user})}
                    >
                        <ImageBackground
                            source={{ uri: player.image }}
                            style={styles.imageBackground}
                            imageStyle={styles.imageStyle}
                        >
                            <View style={styles.overlay}>
                                <Text style={styles.playerName}>{player.name}</Text>
                            </View>
                        </ImageBackground>
                    </TouchableOpacity>
                ))}
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
    },
    scrollContainer: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'flex-start',
    },
    playerButton: {
        width: buttonWidth,
        height: buttonHeight,
        borderRadius: 8,
        overflow: 'hidden',
        marginBottom: 10,
    },
    imageBackground: {
        flex: 1,
        width: '100%',
        height: '100%',
        justifyContent: 'flex-end',
    },
    imageStyle: {
        resizeMode: 'cover',
    },
    overlay: {
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        width: '100%',
        padding: 10,
        alignItems: 'center',
    },
    playerName: {
        color: '#FFFFFF',
        fontSize: 20, // Increased font size
        fontWeight: '600',
    },
});

export default Compare;