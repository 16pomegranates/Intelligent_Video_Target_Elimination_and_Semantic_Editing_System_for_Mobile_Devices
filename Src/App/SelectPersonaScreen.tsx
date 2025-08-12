import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useLanguage } from './context/LanguageContext';
import { builtInPresets, buildInstructionFromPreset } from './utils/personaPresets';

type RouteParams = {
  onApply?: (instruction: string) => void;
};

const SelectPersonaScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { currentLanguage } = useLanguage();
  const params = (route.params || {}) as RouteParams;

  const getLocalizedText = (zhText: string, enText: string) =>
    currentLanguage === 'zh' ? zhText : enText;

  const handleApply = async (presetId: string) => {
    const preset = builtInPresets.find(p => p.id === presetId);
    if (!preset) return;
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    if (typeof params.onApply === 'function') {
      params.onApply(instruction);
    }
    navigation.goBack();
  };

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerTitleWrapper}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>{'<'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{getLocalizedText('选择Persona', 'Select Persona')}</Text>
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        {builtInPresets.map(preset => (
          <ImageBackground
            key={preset.id}
            source={require('../Images/Community/text_background.png')}
            style={styles.card}
            resizeMode="stretch"
          >
            <View style={styles.cardInner}>
              <View style={styles.left}>
                <Image source={preset.icon} style={styles.icon} />
              </View>
              <View style={styles.middle}>
                <Text style={styles.name}>{preset.name}</Text>
                <Text style={styles.tag}>{preset.tag}</Text>
                <Text style={styles.desc}>{preset.description}</Text>
              </View>
              <View style={styles.right}>
                <TouchableOpacity style={styles.applyBtn} onPress={() => handleApply(preset.id)}>
                  <Text style={styles.applyBtnText}>{getLocalizedText('应用', 'Apply')}</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ImageBackground>
        ))}
      </ScrollView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: { flex: 1, width: '100%', height: '100%' },
  content: { padding: 16, paddingBottom: 24 },
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 60,
    backgroundColor: 'transparent',
  },
  backButton: { paddingHorizontal: 12, paddingVertical: 6, height: 40, justifyContent: 'center', alignItems: 'center' },
  backButtonText: { fontSize: 24, color: 'white', fontWeight: 'bold', marginRight: 6 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: 'white', flex: 1, textAlign: 'center', lineHeight: 60 },
  card: {
    width: '106%',
    marginLeft: '-3%',
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
  },
  cardInner: { flex: 1, flexDirection: 'row', padding: 12 },
  left: { width: 64, alignItems: 'center' },
  icon: { width: 40, height: 40, borderRadius: 20, marginTop: 10 },
  middle: { flex: 1, paddingHorizontal: 12 },
  name: { color: 'black', fontSize: 16, fontWeight: 'bold' },
  tag: { color: 'black', fontSize: 12, backgroundColor: '#FFD700', alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12, marginTop: 6 },
  desc: { color: '#222', fontSize: 12, marginTop: 8 },
  right: { width: 90, justifyContent: 'center', alignItems: 'center' },
  applyBtn: { backgroundColor: '#6A5ACD', borderRadius: 18, paddingVertical: 8, paddingHorizontal: 16 },
  applyBtnText: { color: 'white', fontSize: 14, fontWeight: 'bold' },
});

export default SelectPersonaScreen;


