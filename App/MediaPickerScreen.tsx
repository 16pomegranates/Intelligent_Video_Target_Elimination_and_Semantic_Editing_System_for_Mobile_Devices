import React, { useState } from 'react';
import {
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  Button,
  Image,
  Alert,
  Dimensions,
} from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';
import Video from 'react-native-video';
import { Colors } from 'react-native/Libraries/NewAppScreen';
import { useNavigation } from '@react-navigation/native';

const MediaPickerScreen: React.FC = () => {
  const isDarkMode = useColorScheme() === 'dark';
  const [mediaUri, setMediaUri] = useState<string | null>(null);
  const [isVideo, setIsVideo] = useState<boolean>(false);
  const navigation = useNavigation();

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    flex: 1,
  };

  const safePadding = '5%';

  const pickImage = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        includeBase64: false,
      },
      (response) => {
        if (response.didCancel) {
          Alert.alert('提示', '用户取消了选择');
        } else if (response.errorCode) {
          Alert.alert('错误', `选择图片失败: ${response.errorMessage}`);
        } else if (response.assets && response.assets[0].uri) {
          setMediaUri(response.assets[0].uri);
          setIsVideo(false);
        }
      },
    );
  };

  const pickVideo = () => {
    launchImageLibrary(
      {
        mediaType: 'video',
        includeBase64: false,
      },
      (response) => {
        if (response.didCancel) {
          Alert.alert('提示', '用户取消了选择');
        } else if (response.errorCode) {
          Alert.alert('错误', `选择视频失败: ${response.errorMessage}`);
        } else if (response.assets && response.assets[0].uri) {
          setMediaUri(response.assets[0].uri);
          setIsVideo(true);
        }
      },
    );
  };

  const handleEditPress = () => {
    if (mediaUri) {
      navigation.navigate('EditMedia', { mediaUri, isVideo });
    }
  };

  const handleClearMedia = () => {
    setMediaUri(null);
    setIsVideo(false);
  };

  return (
    <View style={backgroundStyle}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />
      <ScrollView style={backgroundStyle}>
        <View style={[styles.container, { paddingHorizontal: safePadding, paddingBottom: safePadding }]}>
          <Text style={[styles.title, { color: isDarkMode ? Colors.white : Colors.black }]}>
            选择并展示图片或视频
          </Text>
          <View style={styles.buttonContainer}>
            <Button title="选择图片" onPress={pickImage} color={isDarkMode ? '#1E90FF' : '#007AFF'} />
            <Button title="选择视频" onPress={pickVideo} color={isDarkMode ? '#1E90FF' : '#007AFF'} />
          </View>
          {mediaUri && (
            <>
              <View style={styles.mediaContainer}>
                {isVideo ? (
                  <Video
                    source={{ uri: mediaUri }}
                    style={styles.media}
                    controls={true}
                    resizeMode="contain"
                    onError={(error: any) => {
                      Alert.alert('错误', `视频播放失败: ${error.message}`);
                    }}
                  />
                ) : (
                  <Image
                    source={{ uri: mediaUri }}
                    style={styles.media}
                    resizeMode="contain"
                  />
                )}
              </View>
              <View style={styles.actionButtonContainer}>
                <Button title="进入编辑" onPress={handleEditPress} color={isDarkMode ? '#1E90FF' : '#007AFF'} />
                <Button title="重新选择" onPress={handleClearMedia} color={isDarkMode ? '#FF4444' : '#FF3B30'} />
              </View>
            </>
          )}
        </View>
      </ScrollView>
    </View>
  );
};

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    marginVertical: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
  },
  mediaContainer: {
    width: '100%',
    alignItems: 'center',
  },
  media: {
    width: width * 0.9,
    height: width * 0.6,
    borderRadius: 10,
  },
  actionButtonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: 20,
  },
});

export default MediaPickerScreen;