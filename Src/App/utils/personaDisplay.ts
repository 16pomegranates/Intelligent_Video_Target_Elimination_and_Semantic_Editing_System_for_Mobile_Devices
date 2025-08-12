import { ImageSourcePropType } from 'react-native';
import { builtInPresets } from './personaPresets';

export interface PersonaDisplayMeta {
  coverImage: ImageSourcePropType;
  author: string;
  downloads: string;
}

// 覆盖图与展示元数据（可按需微调）
export const personaDisplayMap: Record<string, PersonaDisplayMeta> = {
  builtin_rational_lecturer: {
    coverImage: require('../../Images/Community/show.png'),
    author: 'ClipPersona Studio',
    downloads: '2.3k',
  },
  builtin_humorous_barrage: {
    coverImage: require('../../Images/HomePage/card1.png'),
    author: 'CP Lab',
    downloads: '5.1k',
  },
  builtin_romantic_lyrical: {
    coverImage: require('../../Images/Persona/decoration.png'),
    author: 'Moonlight',
    downloads: '1.8k',
  },
  builtin_sports_highlight: {
    coverImage: require('../../Images/MediaPickerScreen/robot2.png'),
    author: 'SportX',
    downloads: '3.9k',
  },
  builtin_tech_review: {
    coverImage: require('../../Images/Persona/computer.png'),
    author: 'TechTalk',
    downloads: '2.7k',
  },
  builtin_cinematic_trailer: {
    coverImage: require('../../Images/Community/show.png'),
    author: 'CinemaCraft',
    downloads: '4.2k',
  },
  builtin_vlog_minimal: {
    coverImage: require('../../Images/SettingScreen/decoration2.png'),
    author: 'SimpleLife',
    downloads: '1.2k',
  },
  builtin_gaming_montage: {
    coverImage: require('../../Images/MediaPickerScreen/robot1.png'),
    author: 'GG Highlights',
    downloads: '6.4k',
  },
  builtin_news_fastcut: {
    coverImage: require('../../Images/SettingScreen/Info.png'),
    author: 'NewsDesk',
    downloads: '2.0k',
  },
  builtin_travel_montage: {
    coverImage: require('../../Images/HomePage/decoration.png'),
    author: 'Traveller',
    downloads: '3.1k',
  },
};

export const getPersonaDisplayMeta = (id: string): PersonaDisplayMeta => {
  const meta = personaDisplayMap[id];
  const preset = builtInPresets.find(p => p.id === id);
  const icon = (preset?.icon) || require('../../Images/HomePage/card1.png');
  return {
    coverImage: icon,
    author: meta?.author || 'ClipPersona',
    downloads: meta?.downloads || '1.0k',
  };
};

export const featuredPersonaIds: string[] = [
  'builtin_cinematic_trailer',
  'builtin_gaming_montage',
  'builtin_romantic_lyrical',
  'builtin_tech_review',
  'builtin_travel_montage',
];

export const getFeaturedPersonas = () => {
  const idSet = new Set(featuredPersonaIds);
  const list = builtInPresets.filter(p => idSet.has(p.id));
  // 若有缺失则补齐
  if (list.length < 5) {
    for (const p of builtInPresets) {
      if (list.length >= 5) break;
      if (!idSet.has(p.id)) list.push(p);
    }
  }
  return list;
};


