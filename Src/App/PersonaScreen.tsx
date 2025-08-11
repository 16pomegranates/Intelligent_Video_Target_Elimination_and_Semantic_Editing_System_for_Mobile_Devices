import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  ScrollView,
  Dimensions,
  TouchableOpacity,
  Image,
  Switch,
  Alert,
} from 'react-native';
import { useLanguage } from './context/LanguageContext'; // 导入 useLanguage
import { PersonaManager, Persona } from './utils/personaManager';

const { width } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

// 默认Persona数据（当没有用户创建的Persona时显示）
const defaultPersonas = [
  {
    id: 'p1',
    icon: require('../Images/HomePage/user.png'),
    name: '理性讲师',
    tag: '理性',
    progress: 0.7,
  },
  {
    id: 'p2',
    icon: require('../Images/HomePage/user.png'),
    name: '搞笑弹幕',
    tag: '搞笑',
    progress: 0.9,
  },
];

const styleCards = [
  {
    id: 's1',
    image: require('../Images/HomePage/card1.png'),
    title: '毒蛇型',
  },
  {
    id: 's2',
    image: require('../Images/HomePage/card1.png'),
    title: '理性讲师',
  },
];

const myShareItems = [
  {
    id: 'share1',
    title: '毒蛇型',
    downloads: 300,
    comments: 15,
    isEnabled: true,
  },
];

const PersonaScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { currentLanguage } = useLanguage();
  const [isSharingEnabled, setIsSharingEnabled] = React.useState(myShareItems[0].isEnabled); // State for the switch
  const [myPersonas, setMyPersonas] = useState(defaultPersonas);
  const [_userPersonas, setUserPersonas] = useState<Persona[]>([]);

  // 加载用户创建的Persona
  useEffect(() => {
    const loadUserPersonas = async () => {
      try {
        const personas = await PersonaManager.getAllPersonas();
        setUserPersonas(personas);
        
        // 如果有用户创建的Persona，使用用户数据；否则使用默认数据
        if (personas.length > 0) {
          const userPersonaData = personas.map(persona => ({
            id: persona.id,
            icon: { uri: persona.imageUri },
            name: persona.name,
            tag: persona.tag,
            progress: persona.progress,
          }));
          setMyPersonas(userPersonaData);
        }
      } catch (error) {
        console.error('Error loading personas:', error);
      }
    };

    loadUserPersonas();
  }, []);

  // 监听页面焦点，当从创建页面返回时重新加载数据
  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadUserPersonas();
    });

    return unsubscribe;
  }, [navigation]);

  const loadUserPersonas = async () => {
    try {
      const personas = await PersonaManager.getAllPersonas();
      setUserPersonas(personas);
      
      if (personas.length > 0) {
        const userPersonaData = personas.map(persona => ({
          id: persona.id,
          icon: { uri: persona.imageUri },
          name: persona.name,
          tag: persona.tag,
          progress: persona.progress,
        }));
        setMyPersonas(userPersonaData);
      } else {
        setMyPersonas(defaultPersonas);
      }
    } catch (error) {
      console.error('Error loading personas:', error);
    }
  };

  const handleDeletePersona = async (personaId: string) => {
    Alert.alert(
      getLocalizedText('确认删除', 'Confirm Delete'),
      getLocalizedText('确定要删除这个Persona吗？', 'Are you sure you want to delete this Persona?'),
      [
        {
          text: getLocalizedText('取消', 'Cancel'),
          style: 'cancel',
        },
        {
          text: getLocalizedText('删除', 'Delete'),
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await PersonaManager.deletePersona(personaId);
              if (success) {
                // 重新加载Persona列表
                await loadUserPersonas();
                Alert.alert(
                  getLocalizedText('成功', 'Success'),
                  getLocalizedText('Persona已删除', 'Persona deleted successfully')
                );
              } else {
                Alert.alert(
                  getLocalizedText('错误', 'Error'),
                  getLocalizedText('删除Persona时出现错误', 'Error deleting Persona')
                );
              }
            } catch (error) {
              console.error('Error deleting persona:', error);
              Alert.alert(
                getLocalizedText('错误', 'Error'),
                getLocalizedText('删除Persona时出现错误', 'Error deleting Persona')
              );
            }
          },
        },
      ]
    );
  };

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  return (
    <ImageBackground
      source={require('../Images/background.png')} // 使用应用的通用背景图
      style={styles.background}
      resizeMode="cover"
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerTitleWrapper}>
          <Text style={styles.headerTitle}>{getLocalizedText('Persona', 'Persona')}</Text>
        </View>

        {/* Create Persona Button */}
        <TouchableOpacity 
          style={styles.createPersonaButton}
          onPress={() => navigation.navigate('CreatePersona' as never)}
        >
          <Text style={styles.createPersonaButtonText}>{getLocalizedText('创建Persona', 'Create Persona')}</Text>
        </TouchableOpacity>

        {/* 我的Persona */}
        <View style={styles.sectionWrapper}>
          <View style={styles.sectionTitleContainer}>
            <Image source={require('../Images/HomePage/instruct.png')} style={styles.sectionTitleIcon} />
            <Text style={styles.sectionTitle}>{getLocalizedText('我的Persona', 'My Persona')}</Text>
          </View>
            <View style={styles.personaListContent}> {/* Inner View for padding */}
              {myPersonas.map(persona => (
                <ImageBackground
                  key={persona.id}
                  source={require('../Images/Community/text_background.png')}
                  style={styles.personaCardBackground}
                  resizeMode="stretch"
                >
                  <View style={styles.personaCardContent}> {/* Inner View for content */}
                    <View style={styles.personaInfo}>
                      <Image source={persona.icon} style={styles.personaIcon} />
                      <View>
                        <Text style={styles.personaName}>{persona.name}</Text>
                        <Text style={styles.personaTag}>{persona.tag}</Text>
                      </View>
                    </View>
                    <View style={styles.progressBarBackground}>
                      <View style={[styles.progressBarFill, { width: `${persona.progress * 100}%` }]} />
                    </View>
                    {/* 删除按钮 - 只对用户创建的Persona显示 */}
                    {persona.id !== 'p1' && persona.id !== 'p2' && (
                      <TouchableOpacity
                        style={styles.deletePersonaButton}
                        onPress={() => handleDeletePersona(persona.id)}
                      >
                        <Text style={styles.deletePersonaButtonText}>×</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </ImageBackground>
              ))}
            </View>
        </View>

        {/* 风格卡管理 */}
        <View style={styles.sectionWrapper}>
          <View style={styles.sectionTitleContainer}>
            <Image source={require('../Images/HomePage/instruct.png')} style={styles.sectionTitleIcon} />
            <Text style={styles.sectionTitle}>{getLocalizedText('风格卡管理', 'Style Card Management')}</Text>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.styleCardsContainer}>
            {styleCards.map(card => (
              <ImageBackground
                key={card.id}
                source={require('../Images/text.png')}
                style={styles.styleCardItemBackground}
                resizeMode="stretch"
              >
                <View style={styles.styleCardItemContent}>
                  <Image source={card.image} style={styles.styleCardImage} resizeMode="cover" />
                  <Text style={styles.styleCardTitle}>{card.title}</Text>
                  <ImageBackground
                    source={require('../Images/HomePage/download_button.png')}
                    style={styles.styleCardDownloadButton}
                    resizeMode="stretch"
                  >
                    <Text style={styles.styleCardDownloadButtonText}>{getLocalizedText('下载', 'Download')}</Text>
                  </ImageBackground>
                </View>
              </ImageBackground>
            ))}
          </ScrollView>
        </View>

        {/* 我的共享 */}
        <View style={styles.sectionWrapper}>
          <View style={styles.sectionTitleContainer}>
            <Image source={require('../Images/HomePage/instruct.png')} style={styles.sectionTitleIcon} />
            <Text style={styles.sectionTitle}>{getLocalizedText('我的共享', 'My Sharing')}</Text>
          </View>
          <ImageBackground
            source={require('../Images/text.png')}
            style={styles.mySharingBackground}
            resizeMode="stretch"
          >
            <View style={styles.mySharingContent}> {/* Inner View for padding */}
              {myShareItems.map(item => (
                <View key={item.id} style={styles.sharingItem}>
                  <View>
                    <Text style={styles.sharingItemTitle}>{item.title}</Text>
                    <Text style={styles.sharingItemStats}>
                      {getLocalizedText('下载:', 'Downloads:')} {item.downloads}  {getLocalizedText('评论:', 'Comments:')} {item.comments}
                    </Text>
                  </View>
                  <Switch
                    trackColor={{ false: "#767577", true: "#81b0ff" }}
                    thumbColor={item.isEnabled ? "#f5dd4b" : "#f4f3f4"}
                    ios_backgroundColor="#3e3e3e"
                    onValueChange={setIsSharingEnabled}
                    value={isSharingEnabled}
                  />
                </View>
              ))}
            </View>
          </ImageBackground>
        </View>

        {/* 成长轨迹 */}
        <View style={styles.sectionWrapper}>
          <View style={styles.sectionTitleContainer}>
            <Image source={require('../Images/HomePage/instruct.png')} style={styles.sectionTitleIcon} />
            <Text style={styles.sectionTitle}>{getLocalizedText('成长轨迹', 'Growth Trajectory')}</Text>
          </View>
          <ImageBackground
            source={require('../Images/text.png')}
            style={styles.growthTrajectoryBackground}
            resizeMode="stretch"
          >
            <View style={styles.growthTrajectoryContent}> {/* Inner View for padding */}
              {/* Placeholder for the graph */}
              <Text style={styles.growthTrajectoryText}>
                {getLocalizedText('里程碑：完成100次调整', 'Milestone: 100 adjustments completed')}
              </Text>
            </View>
          </ImageBackground>
        </View>

      </ScrollView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  scrollContent: {
    flexGrow: 1,
    padding: getRelativeSize(5),
    paddingTop: getRelativeSize(20),
    paddingBottom: getRelativeSize(5),
  },
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: getRelativeSize(14),
    paddingHorizontal: 0,
    marginTop: 0,
    marginBottom: 0,
    backgroundColor: 'transparent',
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7),
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
    lineHeight: getRelativeSize(14),
  },
  createPersonaButton: {
    backgroundColor: '#6A5ACD',
    borderRadius: getRelativeSize(7.5),
    paddingVertical: getRelativeSize(3),
    paddingHorizontal: getRelativeSize(20),
    alignSelf: 'center',
    marginBottom: getRelativeSize(7.5),
    minWidth: getRelativeSize(60),
  },
  createPersonaButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
  },
  sectionWrapper: {
    marginBottom: 30,
    width: '100%',
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    marginLeft: 0,
  },
  sectionTitleIcon: {
    width: 5,
    height: 28,
    marginRight: 8,
    backgroundColor: '#6A5ACD',
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'white',
  },
  personaListBackground: {
    width: '100%',
    borderRadius: 15,
    overflow: 'hidden',
    marginBottom: 20,
  },
  personaListContent: {
    flex: 1,
    padding: 15,
    backgroundColor: 'transparent',
  },
  personaCardBackground: {
    width: '106%',
    marginLeft: '-5%',
    height: 100,
    borderRadius: 10,
    marginBottom: 10,
    overflow: 'hidden',
  },
  personaCardContent: {
    flex: 1,
    padding: 15,
    left: 10,
    backgroundColor: 'transparent',
  },
  personaInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  personaIcon: {
    width: 30,
    height: 30,
    borderRadius: 15,
    marginRight: 10,
  },
  personaName: {
    color: 'black',
    fontSize: 16,
    fontWeight: 'bold',
  },
  personaTag: {
    color: 'black',
    fontSize: 12,
    backgroundColor: '#FFD700',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 15,
    marginLeft: 20,
    top: 5,
    left: -20,
  },
  progressBarBackground: {
    height: 8,
    backgroundColor: '#D3D3D3',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#6A5ACD',
    borderRadius: 4,
  },
  deletePersonaButton: {
    position: 'absolute',
    top: 5,
    right: 5,
    width: 20,
    height: 20,
    backgroundColor: 'rgba(255, 0, 0, 0.8)',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  deletePersonaButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  styleCardsContainer: {
    paddingVertical: 10,
  },
  styleCardItemBackground: {
    width: 150,
    height: 200,
    borderRadius: 15,
    marginRight: 15,
    overflow: 'hidden',
    backgroundColor: 'transparent',
  },
  styleCardItemContent: {
    flex: 1,
    backgroundColor: 'transparent',
    paddingBottom: 10,
  },
  styleCardImage: {
    width: '100%',
    height: 120,
    borderTopLeftRadius: 15,
    borderTopRightRadius: 15,
    marginBottom: 5,
  },
  styleCardTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 5,
  },
  styleCardDownloadButton: {
    width: '100%',
    height: 35,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginTop: 5,
  },
  styleCardDownloadButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  mySharingBackground: {
    width: '100%',
    height: 80,
    borderRadius: 15,
    overflow: 'hidden',
    marginBottom: 20,
  },
  mySharingContent: {
    flex: 1,
    padding: 15,
    backgroundColor: 'transparent',
  },
  sharingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sharingItemTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sharingItemStats: {
    color: '#B0B0B0',
    fontSize: 12,
  },
  growthTrajectoryBackground: {
    width: '100%',
    height: 200,
    borderRadius: 15,
    overflow: 'hidden',
  },
  growthTrajectoryContent: {
    flex: 1,
    padding: 15,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  growthTrajectoryText: {
    color: '#B0B0B0',
    fontSize: 14,
    textAlign: 'center',
  },
});

export default PersonaScreen; 