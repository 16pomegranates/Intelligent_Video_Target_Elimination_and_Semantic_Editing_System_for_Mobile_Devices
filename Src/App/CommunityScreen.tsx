import React, { useMemo, useState } from 'react';
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
import { PersonaManager } from './utils/personaManager';
import { builtInPresets, buildInstructionFromPreset } from './utils/personaPresets';
import { getFeaturedPersonas, getPersonaDisplayMeta } from './utils/personaDisplay';

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
  const [selectedCategory, setSelectedCategory] = useState('全部'); // 默认中文标签

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  // 简化分类（固定少量高层次标签）
  const categories = [
    { zh: '全部', en: 'All' },
    { zh: '娱乐', en: 'Entertainment' },
    { zh: '叙事', en: 'Narrative' },
    { zh: '专业', en: 'Professional' },
  ];

  const mapTagToSimplifiedCategory = (tag: string): '娱乐' | '叙事' | '专业' => {
    // 允许模糊归类
    if (['搞笑', '电竞', '运动'].includes(tag)) return '娱乐';
    if (['温柔', '生活', '风光'].includes(tag)) return '叙事';
    if (['理性', '数码', '资讯', '大片'].includes(tag)) return '专业';
    return '叙事';
  };

  const cardsFromPresets = getFeaturedPersonas().map(p => ({
    id: p.id,
    title: p.name,
    author: getPersonaDisplayMeta(p.id).author,
    downloads: getPersonaDisplayMeta(p.id).downloads,
    description: p.description,
    image: getPersonaDisplayMeta(p.id).coverImage,
    tag: p.tag,
    simpleCategory: mapTagToSimplifiedCategory(p.tag),
  }));

  const handleDownloadPreset = async (presetId: string) => {
    const preset = builtInPresets.find(p => p.id === presetId) || builtInPresets[0];
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    await PersonaManager.addPersona({
      id: Date.now().toString(),
      name: preset.name,
      description: getLocalizedText('来自社区的风格预设', 'Style preset from community'),
      imageUri: '',
      tag: preset.tag,
      progress: 0.8,
      createdAt: new Date().toISOString(),
      instruction,
    });
  };

  const filteredCards = cardsFromPresets.filter(card => {
    const byCategory = selectedCategory === '全部' ? true : card.simpleCategory === selectedCategory;
    if (!byCategory) return false;
    if (!searchQuery.trim()) return true;
    const q = searchQuery.trim().toLowerCase();
    return (
      card.title.toLowerCase().includes(q) ||
      card.description.toLowerCase().includes(q) ||
      String(card.author).toLowerCase().includes(q)
    );
  });

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
        {filteredCards.map((card) => (
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
                <TouchableOpacity style={styles.downloadButton} onPress={() => handleDownloadPreset(card.id)}>
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