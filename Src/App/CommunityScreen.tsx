import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  Image,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Dimensions,
} from 'react-native';
import { useLanguage } from './context/LanguageContext'; // Assuming context is available

const { width } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

const CommunityScreen: React.FC = ({ navigation }: any) => {
  const { currentLanguage } = useLanguage();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('全部'); // Default to '全部'

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  const categories = [
    { zh: '全部', en: 'All' },
    { zh: '搞笑', en: 'Funny' },
    { zh: '抒情', en: 'Lyrical' },
    { zh: '毒舌', en: 'Sarcastic' },
    { zh: '理性', en: 'Rational' },
  ];

  const dummyCards = [
    {
      id: '1',
      title: getLocalizedText('搞笑弹幕', 'Funny Bullet Comments'),
      author: getLocalizedText('张三', 'Zhang San'),
      downloads: '1.2k',
      description: getLocalizedText('一个充满网络梗的幽默风格，适合短视频爆笑场景。', 'A humorous style full of internet memes, suitable for short video hilarious scenes.'),
      image: require('../Images/Community/show.png'),
    },
    {
      id: '2',
      title: getLocalizedText('抒情风格', 'Lyrical Style'),
      author: getLocalizedText('李四', 'Li Si'),
      downloads: '856',
      description: getLocalizedText('温柔细腻的抒情风格，适合情感类短视频内容。', 'Gentle and delicate lyrical style, suitable for emotional short video content.'),
      image: require('../Images/Community/show.png'),
    },
    {
      id: '3',
      title: getLocalizedText('毒舌评论', 'Sarcastic Comments'),
      author: getLocalizedText('王五', 'Wang Wu'),
      downloads: '2.1k',
      description: getLocalizedText('犀利幽默的毒舌风格，让评论更有趣味性。', 'Sharp and humorous sarcastic style, making comments more interesting.'),
      image: require('../Images/Community/show.png'),
    },
    {
      id: '4',
      title: getLocalizedText('理性分析', 'Rational Analysis'),
      author: getLocalizedText('赵六', 'Zhao Liu'),
      downloads: '634',
      description: getLocalizedText('客观理性的分析风格，适合知识类内容。', 'Objective and rational analysis style, suitable for knowledge-based content.'),
      image: require('../Images/Community/show.png'),
    },
    {
      id: '5',
      title: getLocalizedText('网络热梗', 'Internet Memes'),
      author: getLocalizedText('小明', 'Xiao Ming'),
      downloads: '3.5k',
      description: getLocalizedText('结合最新网络热梗的幽默风格，紧跟潮流。', 'Humorous style combining the latest internet memes, keeping up with trends.'),
      image: require('../Images/Community/show.png'),
    },
    {
      id: '6',
      title: getLocalizedText('经典怀旧', 'Classic Nostalgia'),
      author: getLocalizedText('小红', 'Xiao Hong'),
      downloads: '1.8k',
      description: getLocalizedText('充满怀旧情怀的经典风格，唤起美好回忆。', 'Classic style full of nostalgic feelings, evoking beautiful memories.'),
      image: require('../Images/Community/show.png'),
    },
  ];

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerTitleWrapper}>
        <Text style={styles.headerTitle}>{getLocalizedText('社区', 'Community')}</Text>
      </View>

      <View style={styles.searchSortContainer}>
        <View style={styles.searchBox}>
          <TextInput
            style={styles.searchInput}
            placeholder={getLocalizedText('搜索风格卡...', 'Search Style Card...')}
            placeholderTextColor="#888"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <TouchableOpacity style={styles.searchIconContainer}>
            <Text style={styles.searchIcon}>🔍</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.sortButton}>
          <Text style={styles.sortButtonText}>{getLocalizedText('按热度排序', 'Sort by Popularity')}</Text>
          <Text style={styles.sortDropdownIcon}>▼</Text>
        </TouchableOpacity>
      </View>

      <ScrollView horizontal contentContainerStyle={styles.categoryTabsContainer} showsHorizontalScrollIndicator={false}>
        {categories.map((category) => (
          <TouchableOpacity
            key={category.zh}
            style={[
              styles.categoryTab,
              selectedCategory === category.zh && styles.selectedCategoryTab,
            ]}
            onPress={() => setSelectedCategory(category.zh)}
          >
            <Text style={[
              styles.categoryTabText,
              selectedCategory === category.zh && styles.selectedCategoryTabText,
            ]}>
              {getLocalizedText(category.zh, category.en)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {dummyCards.map((card) => (
          <TouchableOpacity
            key={card.id}
            style={styles.card}
            onPress={() => navigation.navigate('StyleCardDetail', { card: card })}
          >
            <Image source={card.image} style={styles.cardImage} resizeMode="cover" />
            <ImageBackground
              source={require('../Images/Community/text_background.png')}
              style={styles.cardContentBackground}
              resizeMode="stretch"
            >
              <View style={styles.cardTextContent}>
                <Text style={styles.cardTitle}>{card.title}</Text>
                <Text style={styles.cardMeta}>
                  {getLocalizedText('作者：', 'Author: ')}{card.author}  {getLocalizedText('下载：', 'Downloads: ')}{card.downloads}
                </Text>
                <Text style={styles.cardDescription}>{card.description}</Text>
                <TouchableOpacity style={styles.downloadButton}>
                  <Text style={styles.downloadButtonText}>{getLocalizedText('下载', 'Download')}</Text>
                  <Image source={require('../Images/Community/download.png')} style={styles.downloadIcon} />
                </TouchableOpacity>
              </View>
            </ImageBackground>
          </TouchableOpacity>
        ))}
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
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: getRelativeSize(20),
    marginBottom: getRelativeSize(2),
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7),
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
  },
  searchSortContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: getRelativeSize(5),
    marginBottom: getRelativeSize(5),
    marginTop: getRelativeSize(5),
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F1F1F', // Deep dark grey
    borderRadius: getRelativeSize(6),
    paddingHorizontal: getRelativeSize(4),
    flex: 1,
    marginRight: getRelativeSize(2.5),
    height: '100%',
  },
  searchInput: {
    flex: 1,
    color: 'white',
    fontSize: getRelativeFontSize(4),
  },
  searchIconContainer: {
    paddingLeft: getRelativeSize(2.5),
  },
  searchIcon: {
    fontSize: getRelativeFontSize(5),
    color: '#999999', // Lighter grey for search icon
  },
  sortButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F1F1F', // Deep dark grey, consistent with searchBox
    borderRadius: getRelativeSize(6),
    paddingHorizontal: getRelativeSize(4),
    paddingVertical: getRelativeSize(2.5),
  },
  sortButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    marginRight: getRelativeSize(1.2),
  },
  sortDropdownIcon: {
    color: 'white',
    fontSize: getRelativeFontSize(3),
  },
  categoryTabsContainer: {
    paddingHorizontal: getRelativeSize(8),
  },
  categoryTab: {
    backgroundColor: '#3A3A3A',
    borderRadius: getRelativeSize(4),
    paddingHorizontal: getRelativeSize(5),
    marginRight: getRelativeSize(4),
  },
  selectedCategoryTab: {
    backgroundColor: '#FFD700',
    borderRadius: getRelativeSize(4),
  },
  categoryTabText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
  },
  selectedCategoryTabText: {
    color: 'black',
    fontSize: getRelativeFontSize(4),
  },
  scrollContent: {
    flexGrow: 1,
    padding: getRelativeSize(4),
    paddingBottom: getRelativeSize(5),
  },
  card: {
    backgroundColor: 'transparent',
    borderRadius: getRelativeSize(4),
    overflow: 'hidden',
    width: width - getRelativeSize(8),
    alignSelf: 'center',
    marginTop: getRelativeSize(5),
    marginBottom: getRelativeSize(5),
  },
  cardImage: {
    width: '105%',
    height: getRelativeSize(45),
    borderTopLeftRadius: getRelativeSize(4),
    borderTopRightRadius: getRelativeSize(4),
    marginLeft: getRelativeSize(-2),
    marginBottom: getRelativeSize(-4), // Negative margin to make the text background overlap slightly
  },
  cardContentBackground: {
    padding: getRelativeSize(6),
    width: '111%',
    justifyContent: 'center',
    paddingTop: getRelativeSize(4), // Add top padding to create space for overlapping
    top: getRelativeSize(-6), // Move up to overlap with the image
    left: getRelativeSize(-4),
  },
  cardTextContent: {
  },
  cardTitle: {
    fontSize: getRelativeFontSize(5),
    fontWeight: 'bold',
    color: '#333333', // Dark color for title
    marginBottom: getRelativeSize(1.2),
  },
  cardMeta: {
    fontSize: getRelativeFontSize(3.5),
    color: '#666666', // Medium grey for meta info
    marginBottom: getRelativeSize(2.5),
  },
  cardDescription: {
    fontSize: getRelativeFontSize(3.5),
    color: '#444444', // Dark grey for description
    marginBottom: getRelativeSize(4),
  },
  downloadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#333333',
    borderRadius: getRelativeSize(5),
    paddingVertical: getRelativeSize(2),
    paddingHorizontal: getRelativeSize(4),
    alignSelf: 'flex-start',
  },
  downloadButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
    marginRight: getRelativeSize(2),
  },
  downloadIcon: {
    width: '5%',
    height: '100%',
    tintColor: 'white',
  },
});

export default CommunityScreen; 