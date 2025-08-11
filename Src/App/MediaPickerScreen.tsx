import React, { useState } from 'react';
import {
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  Alert,
  Dimensions,
  TouchableOpacity,
  Image,
  ImageBackground,
  ActivityIndicator,
} from 'react-native';
import { launchImageLibrary, launchCamera } from 'react-native-image-picker';
import Video from 'react-native-video';
import { Colors } from 'react-native/Libraries/NewAppScreen';
import { useNavigation, NavigationProp, ParamListBase } from '@react-navigation/native';
import { useLanguage } from './context/LanguageContext';

// API配置
const API_CONFIG = {
  BASE_URL: 'http://192.168.74.174:8000',
  ENDPOINTS: {
    UPLOAD_VIDEO: '/upload-video',
  }
};

// 导航参数类型定义
type RootStackParamList = {
  EditMedia: {
    mediaUri: string;
    isVideo: boolean;
  };
};

const MediaPickerScreen: React.FC = () => {
  const isDarkMode = useColorScheme() === 'dark';
  const [mediaUri, setMediaUri] = useState<string | null>(null);
  const [isVideo, setIsVideo] = useState<boolean>(false);
  const [mediaDimensions, setMediaDimensions] = useState<{ width: number; height: number } | null>(null);
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();
  const screenWidth = Dimensions.get('window').width;
  const { currentLanguage } = useLanguage();

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  const pickVideo = async () => {
    launchImageLibrary(
      {
        mediaType: 'video',
        includeBase64: false,
      },
      (response) => {
        if (response.didCancel) {
          return;
        } else if (response.errorCode) {
          Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`选择视频失败: ${response.errorMessage}`, `Failed to select video: ${response.errorMessage}`));
        } else if (response.assets && response.assets[0].uri) {
          setMediaUri(response.assets[0].uri);
          setIsVideo(true);
          if (response.assets[0].width && response.assets[0].height) {
            setMediaDimensions({
              width: response.assets[0].width,
              height: response.assets[0].height,
            });
          } else {
            setMediaDimensions(null);
          }
        }
      },
    );
  };

  const captureVideo = async () => {
    launchCamera(
      {
        mediaType: 'video',
        includeBase64: false,
      },
      (response) => {
        if (response.didCancel) {
          return;
        } else if (response.errorCode) {
          Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`录制视频失败: ${response.errorMessage}`, `Failed to record video: ${response.errorMessage}`));
        } else if (response.assets && response.assets[0].uri) {
          setMediaUri(response.assets[0].uri);
          setIsVideo(true);
          if (response.assets[0].width && response.assets[0].height) {
            setMediaDimensions({
              width: response.assets[0].width,
              height: response.assets[0].height,
            });
          } else {
            setMediaDimensions(null);
          }
        }
      },
    );
  };

  const handleEditPress = () => {
    if (!mediaUri) {
      Alert.alert(getLocalizedText('提示', 'Tip'), getLocalizedText('请先选择视频', 'Please select a video first'));
      return;
    }

    navigation.navigate('EditMedia', {
      mediaUri,
      isVideo,
    });
  };

  const handleClearMedia = () => {
    setMediaUri(null);
    setIsVideo(false);
    setMediaDimensions(null);
  };

  const boxWidth = screenWidth * 0.9;
  let dynamicVideoBoxHeight = height * 0.5; // Default height

  if (mediaUri && mediaDimensions) {
    const aspectRatio = mediaDimensions.width / mediaDimensions.height;
    dynamicVideoBoxHeight = boxWidth / aspectRatio;
  }

  // Ensure height is within reasonable bounds
  dynamicVideoBoxHeight = Math.min(dynamicVideoBoxHeight, height * 0.7); // Max height
  dynamicVideoBoxHeight = Math.max(dynamicVideoBoxHeight, height * 0.3); // Min height

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor="transparent"
        translucent
      />
      {/* 顶部标题 */}
      <View style={styles.pageHeaderContainer}>
        <Text style={styles.pageHeaderTitle}>{getLocalizedText('剪辑', 'Edit')}</Text>
      </View>

      <View style={styles.mainContentContainer}>
        <View style={[styles.videoDisplayBox, { height: dynamicVideoBoxHeight }]}>
          {mediaUri ? (
            isVideo ? (
              <Video
                source={{ uri: mediaUri }}
                style={styles.mediaContent}
                controls={true}
                resizeMode="contain"
                onError={(error: any) => {
                  Alert.alert('错误', `视频播放失败: ${error.message}`);
                }}
              />
            ) : (
              <Image
                source={{ uri: mediaUri }}
                style={styles.mediaContent}
                resizeMode="contain"
              />
            )
          ) : (
            <Text style={styles.placeholderText}>{getLocalizedText('视频/图片将在此显示', 'Video/Image will appear here')}</Text>
          )}
        </View>

        {!mediaUri ? (
          <View style={styles.initialButtonContainer}>
            <TouchableOpacity
              style={styles.customButton}
              onPress={pickVideo}
            >
              <Text style={styles.buttonText}>{getLocalizedText('选择视频', 'Select Video')}</Text>
              <Image
                source={require('../Images/MediaPickerScreen/robot1.png')}
                style={[styles.robotIcon, styles.robotIconLeft]}
              />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.customButton}
              onPress={captureVideo}
            >
              <Text style={styles.buttonText}>{getLocalizedText('录制视频', 'Record Video')}</Text>
              <Image
                source={require('../Images/MediaPickerScreen/robot2.png')}
                style={[styles.robotIcon, styles.robotIconRight]}
              />
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.actionButtonContainer}>
            <TouchableOpacity
              style={[styles.globalButton, { backgroundColor: 'rgb(120,121,241)' }]}
              onPress={handleEditPress}
              activeOpacity={0.8}
            >
              <Text style={styles.globalButtonLabel}>{getLocalizedText('编辑', 'Edit')}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.globalButton, { backgroundColor: '#B0B0B0' }]}
              onPress={handleClearMedia}
              activeOpacity={0.8}
            >
              <Text style={styles.globalButtonLabel}>{getLocalizedText('重选', 'Reselect')}</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ImageBackground>
  );
};

const { width, height } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  mainContentContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: getRelativeSize(2.5),
    paddingBottom: 0,
  },
  videoDisplayBox: {
    width: width * 0.9,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: getRelativeSize(2.5),
  },
  mediaContent: {
    width: '100%',
    height: '100%',
    borderRadius: getRelativeSize(2.5),
  },
  placeholderText: {
    color: 'white',
    fontSize: getRelativeFontSize(5),
  },
  initialButtonContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    gap: getRelativeSize(5),
    marginTop: getRelativeSize(7.5),
  },
  customButton: {
    width: width * 0.8,
    height: getRelativeSize(15),
    backgroundColor: 'rgb(120, 121, 241)',
    borderRadius: getRelativeSize(7.5),
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: getRelativeSize(15),
    position: 'relative',
  },
  buttonText: {
    color: 'white',
    fontSize: getRelativeFontSize(5.5),
    fontWeight: '600',
  },
  robotIcon: {
    width: getRelativeSize(25),
    height: getRelativeSize(25),
    resizeMode: 'contain',
    position: 'absolute',
    top: '5%',
    transform: [{ translateY: getRelativeSize(-5) }],
  },
  robotIconLeft: {
    left: getRelativeSize(-3),
  },
  robotIconRight: {
    right: getRelativeSize(-3),
  },
  actionButtonContainer: {
    flexDirection: 'row',
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: getRelativeSize(10),
  },
  imageActionButton: {
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: getRelativeSize(5),
  },
  actionButtonImage: {
    width: getRelativeSize(20),
    height: getRelativeSize(20),
    resizeMode: 'contain',
    marginBottom: getRelativeSize(2),
  },
  actionButtonLabel: {
    color: 'white',
    fontSize: getRelativeFontSize(5),
    fontWeight: '600',
    textAlign: 'center',
  },
  pageHeaderContainer: { // New page header container style
    width: '100%',
    alignItems: 'center',
    position: 'absolute',
    top: getRelativeSize(12.5), // This might need further adjustment after testing on device
    zIndex: 10,
    marginBottom: 0, // Consistent spacing below the title
  },
  pageHeaderTitle: { // New page header title style
    fontSize: getRelativeFontSize(7), // Standardized font size
    fontWeight: 'bold',
    color: 'white',
    top: getRelativeSize(8.75),
  },
  globalButton: {
    minWidth: getRelativeSize(27.5),
    height: getRelativeSize(12),
    borderRadius: getRelativeSize(6),
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: getRelativeSize(4.5),
    paddingHorizontal: getRelativeSize(7),
    shadowColor: '#000',
    shadowOffset: { width: 0, height: getRelativeSize(0.5) },
    shadowOpacity: 0.12,
    shadowRadius: getRelativeSize(1),
    elevation: 3,
  },
  globalButtonLabel: {
    color: 'white',
    fontSize: getRelativeFontSize(5),
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 1,
  },
});

export default MediaPickerScreen;
