import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  Dimensions,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ImageBackground,
  Keyboard,
  PermissionsAndroid,
} from 'react-native';
import Video, { VideoRef } from 'react-native-video';
import ChatScreen from './components/ChatScreen';
import RNFS from 'react-native-fs';
import { CameraRoll } from '@react-native-camera-roll/camera-roll';
import { checkStoragePermissions, requestStoragePermissions } from './utils/permissionManager';
import { saveDraftVideo } from './utils/draftVideoManager';
import { useFocusEffect } from '@react-navigation/native';
import { PersonaManager } from './utils/personaManager';
import { useLanguage } from './context/LanguageContext';

// API配置
const API_CONFIG = {
  BASE_URL: 'http://139.224.33.240:8000',
  ENDPOINTS: {
    PROCESS_VIDEO: '/process-video',
    CHECK_FILE: '/check-file'
  }
};

interface RouteParams {
  mediaUri: string;
  isVideo: boolean;
}

interface Props {
  route: {
    params: RouteParams;
  };
  navigation: any;
}

interface VideoError {
  error: {
    errorString?: string;
    errorException?: string;
    errorStackTrace?: string;
    errorCode?: string;
    error?: string;
    domain?: string;
  };
  target?: number;
}

const EditMediaScreen: React.FC<Props> = ({ route, navigation }) => {
  const { mediaUri: initialMediaUri, isVideo } = route.params;
  // const _isDarkMode = useColorScheme() === 'dark';
  const [isPlaying, setIsPlaying] = useState(true);
  const videoRef = useRef<VideoRef>(null);
  const [videoPath, setVideoPath] = useState<string>(initialMediaUri);
  const [currentMediaUri, setCurrentMediaUri] = useState<string>(initialMediaUri);
  const [currentProcessedVideo, setCurrentProcessedVideo] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [lastUploadedUri, setLastUploadedUri] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{
    id: string;
    text: string;
    isUser: boolean;
    type: 'text' | 'audio' | 'preview';
    videoPath?: string;
    onSave?: () => Promise<void>;
    onDiscard?: () => Promise<void>;
    onPreview?: () => void;
  }>>([]);
  const { currentLanguage } = useLanguage();
  const [lastAppliedInstruction, setLastAppliedInstruction] = useState<string | null>(null);

  // 辅助函数：根据当前语言获取文本
  const getLocalizedText = useCallback((zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  }, [currentLanguage]);

  // 新增：自动保存草稿的函数
  const autoSaveDraft = useCallback(async () => {
    if (currentProcessedVideo) {
      console.log(getLocalizedText('检测到未保存的草稿视频，尝试自动保存...', 'Unsaved draft video detected, attempting auto-save...'));
      const draftName = getLocalizedText(`草稿_${new Date().toLocaleDateString()}_${new Date().toLocaleTimeString()}`, `Draft_${new Date().toLocaleDateString()}_${new Date().toLocaleTimeString()}`);
      const savedDraft = await saveDraftVideo({
        name: draftName,
        path: currentProcessedVideo,
      });

      if (savedDraft) {
        console.log('临时草稿视频自动保存成功:', savedDraft.path);
        // 自动保存后，清理 currentProcessedVideo，避免重复保存或影响下次编辑
        setCurrentProcessedVideo(null);
      } else {
        console.error('临时草稿视频自动保存失败。');
      }
    }
  }, [currentProcessedVideo, getLocalizedText]);

  // 使用 useFocusEffect 在屏幕失去焦点时触发自动保存
  useFocusEffect(
    useCallback(() => {
      return () => {
        // 当屏幕失去焦点或组件卸载时，执行自动保存
        autoSaveDraft();
      };
    }, [autoSaveDraft]) // 依赖 autoSaveDraft 确保在它改变时 effect 会重新注册
  );

  useEffect(() => {
    if (isVideo && initialMediaUri) {
      setVideoPath(initialMediaUri);
    }
  }, [initialMediaUri, isVideo]);

  // 检查权限状态
  useEffect(() => {
    // 仅在 Android 上确保权限，iOS 默认允许
    checkStoragePermissions();
  }, []);

  useEffect(() => {
    const keyboardWillShowListener = Keyboard.addListener(
      Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow',
      () => {
        // 当键盘显示时隐藏底部导航栏
        navigation.getParent()?.setOptions({
          tabBarStyle: { display: 'none' }
        });
      }
    );
    const keyboardWillHideListener = Keyboard.addListener(
      Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide',
      () => {
        // 当键盘隐藏时显示底部导航栏
        navigation.getParent()?.setOptions({
          tabBarStyle: {
            display: 'flex',
            height: 60,
            paddingBottom: 10,
            paddingTop: 5,
          }
        });
      }
    );

    return () => {
      keyboardWillShowListener.remove();
      keyboardWillHideListener.remove();
      // 确保在组件卸载时恢复底部导航栏
      navigation.getParent()?.setOptions({
        tabBarStyle: {
          display: 'flex',
          height: 60,
          paddingBottom: 10,
          paddingTop: 5,
        }
      });
    };
  }, [navigation]);

  // 保留占位，避免未来需求时大改
  const handleMediaLayout = () => {};

  const checkAndUploadVideo = async (uri: string): Promise<boolean> => {
    if (!uri) {
      console.error('视频URI为空');
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText('无效的视频路径', 'Invalid video path'));
      return false;
    }

    if (uri === lastUploadedUri) {
      console.log('视频已经上传过，无需重新上传');
      return true;
    }

    setIsUploading(true);
    try {
      console.log('准备上传视频:', uri);
      // 检查文件是否存在
      try {
        const fileExists = await RNFS.exists(uri.replace('file://', ''));
        if (!fileExists) {
          throw new Error('视频文件不存在');
        }
        console.log('本地文件检查通过');
      } catch (error: any) {
        console.error('文件检查失败:', error);
        throw new Error(`文件检查失败: ${error.message}`);
      }

      // 先检查文件是否已经上传
      const filename = uri.split('/').pop() || '';
      console.log('检查文件是否已上传:', filename);

      try {
        const checkResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHECK_FILE}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ filename }),
        });

        if (!checkResponse.ok) {
          throw new Error(`服务器响应错误: ${checkResponse.status}`);
        }

        const checkData = await checkResponse.json();
        console.log('检查文件响应:', checkData);

        if (checkData.status === 'success' && checkData.exists) {
          console.log('文件已存在于服务器');
          setLastUploadedUri(uri);
          return true;
        }
      } catch (error) {
        console.error('检查文件状态失败:', error);
        // 继续尝试上传
      }

      // 如果文件不存在，则上传
      console.log('开始构建上传表单');
      const formData = new FormData();
      formData.append('video', {
        uri: uri,
        type: 'video/mp4',
        name: filename,
      } as any);

      console.log('发送上传请求');
      const response = await fetch(`${API_CONFIG.BASE_URL}/upload-video`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('上传响应错误:', {
          status: response.status,
          statusText: response.statusText,
          errorText
        });
        throw new Error(`上传失败: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log('上传响应:', data);

      if (data.status === 'success') {
        console.log('视频上传成功');
        setLastUploadedUri(uri);
        return true;
      } else {
        throw new Error(data.message || '上传失败');
      }
    } catch (error: any) {
      console.error('上传视频失败:', error);
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`上传视频失败: ${error.message}`, `Video upload failed: ${error.message}`));
      return false;
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectVideo = async (videoPath: string) => {
    try {
      console.log('开始选择视频:', videoPath);

      // 检查文件路径格式
      if (!videoPath.startsWith('file://')) {
        videoPath = 'file://' + (videoPath.startsWith('/') ? videoPath : '/' + videoPath);
      }
      console.log('格式化后的视频路径:', videoPath);

      // 更新显示的视频
      setVideoPath(videoPath);
      // 更新待编辑的视频路径
      setCurrentMediaUri(videoPath);
      // 重置上传状态
      setLastUploadedUri(null);
      setIsPlaying(true);

      // 添加选择确认消息
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: getLocalizedText('已选择此版本视频进行后续编辑', 'This version of the video has been selected for further editing'),
        isUser: false,
        type: 'text'
      }]);

      // 预先上传新选择的视频
      console.log('开始预上传视频');
      const uploadSuccess = await checkAndUploadVideo(videoPath);
      if (!uploadSuccess) {
        console.error('预上传视频失败');
        Alert.alert(getLocalizedText('警告', 'Warning'), getLocalizedText('视频预上传失败，可能影响后续编辑操作', 'Video pre-upload failed, which may affect subsequent editing operations'));
      } else {
        console.log('预上传视频成功');
      }
    } catch (error: any) {
      console.error('选择视频时出错:', error);
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`选择视频失败: ${error.message}`, `Failed to select video: ${error.message}`));
    }
  };

  // 修改下载视频的函数
  const downloadVideo = async (url: string): Promise<string | null> => {
    try {
      console.log('开始下载视频:', url);

      // 检查权限
      if (Platform.OS === 'android') {
        const writePermission = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          {
            title: getLocalizedText('存储权限', 'Storage Permission'),
            message: getLocalizedText('需要存储权限才能下载视频', 'Storage permission is required to download videos.'),
            buttonNeutral: getLocalizedText('稍后询问', 'Ask Later'),
            buttonNegative: getLocalizedText('取消', 'Cancel'),
            buttonPositive: getLocalizedText('确定', 'OK')
          }
        );
        if (writePermission !== PermissionsAndroid.RESULTS.GRANTED) {
          throw new Error(getLocalizedText('需要存储权限才能下载视频', 'Storage permission required to download video'));
        }
      }

      // 创建本地文件路径
      const timestamp = new Date().getTime();
      const localPath = `${RNFS.CachesDirectoryPath}/temp_video_${timestamp}.mp4`;

      console.log('本地保存路径:', localPath);

      // 下载文件
      const response = await RNFS.downloadFile({
        fromUrl: url,
        toFile: localPath,
        background: true,
        discretionary: true,
        progress: (res) => {
          const progressPercent = ((res.bytesWritten / res.contentLength) * 100).toFixed(0);
          console.log(`下载进度: ${progressPercent}%`);
        }
      }).promise;

      console.log('下载响应:', response);

      // 验证下载是否成功
      const fileExists = await RNFS.exists(localPath);
      if (!fileExists) {
        throw new Error('下载完成但文件不存在');
      }

      const fileSize = await RNFS.stat(localPath);
      console.log('下载文件大小:', fileSize.size);

      if (fileSize.size === 0) {
        throw new Error('下载的文件大小为0');
      }

      return localPath;
    } catch (error: any) {
      console.error('下载视频失败:', error);
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`下载视频失败: ${error.message}`, `Video download failed: ${error.message}`));
      throw new Error(getLocalizedText(`下载视频失败: ${error.message}`, `Video download failed: ${error.message}`));
    }
  };

  // 预览/放弃逻辑现已通过消息卡片入口触发选择版本，无需单独按钮

  const handleExportVideo = async () => {
    if (!videoPath) {
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText('没有可导出的视频', 'No video to export'));
      return;
    }

    try {
      console.log('开始导出视频:', videoPath);

      // 检查权限
      const hasPermission = await requestStoragePermissions();
      if (!hasPermission) {
        throw new Error(getLocalizedText('需要存储权限才能导出视频', 'Storage permission required to export video'));
      }

      // 确保文件路径格式正确
      let filePath = videoPath;
      if (!filePath.startsWith('file://')) {
        filePath = 'file://' + (filePath.startsWith('/') ? filePath : '/' + filePath);
      }

      // 检查文件是否存在
      const fileExists = await RNFS.exists(filePath.replace('file://', ''));
      if (!fileExists) {
        throw new Error('视频文件不存在');
      }

      // 使用CameraRoll保存到相册
      await CameraRoll.save(filePath, {
        type: 'video',
        album: 'ClipPersona'
      });

      Alert.alert(getLocalizedText('成功', 'Success'), getLocalizedText('视频已成功导出到相册', 'Video successfully exported to album'));
    } catch (error: any) {
      console.error('导出视频失败:', error);
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`导出视频失败: ${error.message}`, `Video export failed: ${error.message}`));
    }
  };

  const handleProcessedVideo = async (localPath: string) => {
    // 记录当前处理结果路径
    setCurrentProcessedVideo(localPath);

    // 添加消息
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      text: getLocalizedText('视频处理完成，点击"选择"可以使用此版本继续编辑', 'Video processing complete, click "Select" to continue editing with this version'),
      isUser: false,
      type: 'preview',
      videoPath: localPath,
      onPreview: () => handleSelectVideo(localPath)
    }]);
  };

  const handleNaturalLanguageCommand = async (command: string) => {
    if (!currentMediaUri) {
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText('没有选择视频', 'No video selected'));
      return;
    }

    if (isProcessing) {
      Alert.alert(getLocalizedText('提示', 'Tip'), getLocalizedText('视频正在处理中，请稍候...', 'Video is processing, please wait...'));
      return;
    }

    setIsProcessing(true);
    try {
      // 检查并上传视频
      const uploadSuccess = await checkAndUploadVideo(currentMediaUri);
      if (!uploadSuccess) {
        throw new Error('视频上传失败');
      }

      // 首先发送到 nlp_parser 进行解析
      const nlpResponse = await fetch(`${API_CONFIG.BASE_URL}/process-video`, {
        method: 'POST',
        body: (() => {
          const formData = new FormData();
          formData.append('video', {
            uri: currentMediaUri,
            type: 'video/mp4',
            name: currentMediaUri.split('/').pop() || 'video.mp4',
          } as any);
          formData.append('instruction', command);
          return formData;
        })(),
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json',
        },
      });

      if (!nlpResponse.ok) {
        const errorBody = await nlpResponse.text();
        console.error(
          `处理指令失败: 状态码 ${nlpResponse.status}, 状态文本: ${nlpResponse.statusText}, 响应体: ${errorBody}`
        );
        throw new Error(
          `处理指令失败: ${nlpResponse.status} ${nlpResponse.statusText} - ${errorBody.substring(0, 100)}...`
        );
      }

      const data = await nlpResponse.json();

      // 显示 NLP 解析的回复
      if (data.message) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          text: data.message,
          isUser: false,
          type: 'text'
        }]);
      }

      if (data.status === 'success' && data.output_path) {
        try {
          const videoUrl = `${API_CONFIG.BASE_URL}${data.output_path}`;
          const localPath = await downloadVideo(videoUrl);
          if (!localPath) {
            throw new Error('下载处理后的视频失败');
          }
          await handleProcessedVideo(localPath);
        } catch (error: any) {
          console.error('处理视频结果时出错:', error);
          Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`处理视频失败: ${error.message}`, `Video processing failed: ${error.message}`));
        }
      } else {
        Alert.alert(getLocalizedText('错误', 'Error'), data.message || getLocalizedText('处理视频失败', 'Video processing failed'));
      }
    } catch (error: any) {
      console.error('处理视频时出错:', error.message, error.stack);
      Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText(`处理视频失败: ${error.message}`, `Video processing failed: ${error.message}`));
    } finally {
      setIsProcessing(false);
    }
  };

  // 修改视频错误处理函数
  const handleVideoError = (e: Readonly<VideoError>) => {
    console.error('视频播放错误:', e.error);
    Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText('视频播放失败，请重试', 'Video playback failed, please try try again'));
  };

  // 修改保存和放弃的处理函数
  // 保存逻辑已内置在导出与草稿保存流程中

  // 放弃修改逻辑已由聊天消息操作控制

  // 添加导出按钮组件
  const ExportButton = () => (
    <TouchableOpacity style={[styles.toolbarButton, styles.btnExport]} onPress={handleExportVideo}>
      <Text style={styles.toolbarButtonText}>{getLocalizedText('导出', 'Export')}</Text>
    </TouchableOpacity>
  );

  const PersonaButton = () => (
    <TouchableOpacity
      style={[styles.toolbarButton, styles.btnPersona]}
      onPress={() => {
        navigation.navigate('SelectPersona', {
          onApply: (instruction: string) => {
            setLastAppliedInstruction(instruction);
            const match = instruction.match(/使用风格:\s*([^；\n]+)/);
            const name = match ? match[1] : getLocalizedText('已应用风格', 'Style Applied');
            setMessages(prev => [
              ...prev,
              {
                id: Date.now().toString(),
                text: getLocalizedText(`已应用Persona: ${name}`, `Applied Persona: ${name}`),
                isUser: false,
                type: 'text',
              },
            ]);
            handleNaturalLanguageCommand(instruction);
          },
        });
      }}
    >
      <Text style={styles.toolbarButtonText}>{getLocalizedText('Persona', 'Persona')}</Text>
    </TouchableOpacity>
  );

  const SavePersonaButton = () => (
    <TouchableOpacity
      style={[styles.toolbarButton, styles.btnSave]}
      onPress={async () => {
        try {
          const instruction = lastAppliedInstruction || '';
          const nameMatch = instruction ? instruction.match(/使用风格:\s*([^；\n]+)/) : null;
          const name = nameMatch ? nameMatch[1] : getLocalizedText('我的Persona', 'My Persona');
          const description = instruction ? instruction.slice(0, 120) : getLocalizedText('从当前剪辑偏好生成', 'Generated from current editing preference');
          const newPersona = {
            id: Date.now().toString(),
            name,
            description,
            imageUri: '',
            tag: getLocalizedText('自定义', 'Custom'),
            progress: 0.8,
            createdAt: new Date().toISOString(),
            instruction,
          };
          const ok = await PersonaManager.addPersona(newPersona as any);
          if (ok) {
            setMessages(prev => [
              ...prev,
              {
                id: (Date.now() + 1).toString(),
                text: getLocalizedText('已保存为Persona', 'Saved as Persona'),
                isUser: false,
                type: 'text',
              },
            ]);
            Alert.alert(getLocalizedText('成功', 'Success'), getLocalizedText('Persona 已保存', 'Persona saved'));
          } else {
            Alert.alert(getLocalizedText('错误', 'Error'), getLocalizedText('保存Persona失败', 'Failed to save Persona'));
          }
        } catch (e: any) {
          Alert.alert(getLocalizedText('错误', 'Error'), e.message || getLocalizedText('保存Persona失败', 'Failed to save Persona'));
        }
      }}
    >
      <Text style={styles.toolbarButtonText}>{getLocalizedText('存为Persona', 'Save Persona')}</Text>
    </TouchableOpacity>
  );

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.container}
      resizeMode="cover"
    >
      <View style={styles.headerTitleWrapper}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>{'<'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{getLocalizedText('项目编辑', 'Project Edit')}</Text>
      </View>
      <KeyboardAvoidingView
        style={styles.innerContainer}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        <View style={styles.videoContainer}>
          <View style={styles.topToolbar}>
            <SavePersonaButton />
            <PersonaButton />
            <ExportButton />
          </View>
          <ImageBackground
            source={require('../Images/EditMediaScreen/show_video.png')}
            style={styles.videoFrame}
            resizeMode="stretch"
          >

            {isVideo && videoPath && (
              <Video
                ref={videoRef}
                source={{ uri: videoPath }}
                style={styles.video}
                resizeMode="contain"
                controls={true}
                // 可按需添加 onLoad / onProgress
                onLayout={handleMediaLayout}
                onError={handleVideoError}
                paused={!isPlaying || isProcessing}
              />
            )}
            {!isVideo && (
              <Image
                source={{ uri: currentMediaUri }}
                style={styles.video}
                resizeMode="contain"
                onLayout={handleMediaLayout}
              />
            )}
            {isProcessing && (
              <View style={styles.processingOverlay}>
                <Text style={styles.processingText}>{getLocalizedText('处理中...', 'Processing...')}</Text>
              </View>
            )}

          </ImageBackground>
        </View>

        <View style={styles.chatContainer}>
          <ChatScreen
            onSendCommand={handleNaturalLanguageCommand}
            disabled={isProcessing || isUploading}
            messages={messages}
            setMessages={setMessages}
          />
        </View>
      </KeyboardAvoidingView>
    </ImageBackground>
  );
};

const { width } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  innerContainer: {
    flex: 1,
    paddingTop: 4,
  },
  videoContainer: {
    width: width,
    height: width * 0.6,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  videoFrame: {
    marginTop: -90,
    width: width,
    height: width * 9 / 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  video: {
    width: '85%',
    height: '85%',
  },
  chatContainer: {
    marginTop: 12,
    flex: 1,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: 'hidden',
  },
  processingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  processingText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  topToolbar: {
    position: 'absolute',
    top: -150,
    width: width,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    zIndex: 2,
  },
  toolbarButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginHorizontal: 6,
  },
  btnExport: { backgroundColor: '#4CAF50' },
  btnPersona: { backgroundColor: '#6A5ACD' },
  btnSave: { backgroundColor: '#FF9800' },
  toolbarButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: getRelativeSize(44),
    paddingHorizontal: 0,
    marginTop: 0,
    marginBottom: 0,
    backgroundColor: 'transparent',
  },
  backButton: {
    paddingHorizontal: getRelativeSize(3.75),
    paddingVertical: getRelativeSize(1.25),
    height: getRelativeSize(14),
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: getRelativeFontSize(7),
    color: 'white',
    fontWeight: 'bold',
    marginRight: getRelativeSize(2.5),
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7),
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
    lineHeight: getRelativeSize(14),
    left: getRelativeSize(-5),
  },
  scrollContent: {
    flexGrow: 1,
    padding: getRelativeSize(5),
    paddingTop: getRelativeSize(5),
    paddingBottom: getRelativeSize(5),
  },
});

export default EditMediaScreen;

