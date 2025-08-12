import { ImageSourcePropType } from 'react-native';

export type PersonaTone = 'rational' | 'humorous' | 'romantic';

export interface SubtitleStylePreset {
  fontFamily: string;
  fontSize: number;
  color: string;
  position: 'top' | 'bottom' | 'center';
  animation: 'none' | 'pop' | 'slide' | 'bounce';
}

export interface CutStylePreset {
  pace: 'slow' | 'medium' | 'fast';
  jumpCut: boolean;
  zoomPan: boolean;
}

export interface BgmPreset {
  mood: 'calm' | 'upbeat' | 'cinematic';
  volume: number; // 0-1
}

export interface OverlayPreset {
  captions: boolean;
  stickers: boolean;
  barrage: boolean;
}

export interface PersonaStylePreset {
  tone: PersonaTone;
  subtitle: SubtitleStylePreset;
  cut: CutStylePreset;
  bgm: BgmPreset;
  overlay: OverlayPreset;
  transitions: 'none' | 'smooth' | 'flashy';
}

export interface PresetPersona {
  id: string;
  name: string;
  tag: string;
  icon: ImageSourcePropType;
  description: string;
  stylePreset: PersonaStylePreset;
}

export const buildInstructionFromPreset = (name: string, preset: PersonaStylePreset): string => {
  const parts: string[] = [];
  parts.push(`使用风格: ${name}`);
  // 语气
  if (preset.tone === 'rational') {
    parts.push('整体语气偏理性、严谨的讲解风格');
  }
  if (preset.tone === 'humorous') {
    parts.push('整体语气偏幽默、弹幕式调侃风格');
  }
  if (preset.tone === 'romantic') {
    parts.push('整体语气偏抒情浪漫、温柔风格');
  }
  // 字幕
  parts.push(
    `字幕: 字体${preset.subtitle.fontFamily}, 大小${preset.subtitle.fontSize}, 颜色${preset.subtitle.color}, 位置${preset.subtitle.position}, 动画${preset.subtitle.animation}`
  );
  // 剪辑
  parts.push(
    `剪辑: 节奏${preset.cut.pace}, 跳剪${preset.cut.jumpCut ? '开启' : '关闭'}, 视角运动${preset.cut.zoomPan ? '适度运镜' : '无运镜'}`
  );
  // 转场
  parts.push(`转场: ${preset.transitions}`);
  // 叠加
  parts.push(
    `叠加: ${preset.overlay.captions ? '保留字幕' : '无字幕'}${preset.overlay.barrage ? '，增加弹幕风格文案' : ''}${preset.overlay.stickers ? '，适当贴纸' : ''}`
  );
  // BGM
  parts.push(`BGM: 氛围${preset.bgm.mood}, 音量${Math.round(preset.bgm.volume * 100)}%`);
  parts.push('请按以上风格对当前视频做统一剪辑处理。');
  return parts.join('；');
};

export const builtInPresets: PresetPersona[] = [
  {
    id: 'builtin_rational_lecturer',
    name: '理性讲师',
    tag: '理性',
    icon: require('../../Images/Persona/teach.png'),
    description: '严谨讲解，信息密度高，字幕清晰稳重。',
    stylePreset: {
      tone: 'rational',
      subtitle: {
        fontFamily: 'PingFang SC',
        fontSize: 28,
        color: '#FFFFFF',
        position: 'bottom',
        animation: 'none',
      },
      cut: {
        pace: 'medium',
        jumpCut: false,
        zoomPan: false,
      },
      transitions: 'smooth',
      overlay: {
        captions: true,
        stickers: false,
        barrage: false,
      },
      bgm: {
        mood: 'cinematic',
        volume: 0.2,
      },
    },
  },
  {
    id: 'builtin_humorous_barrage',
    name: '搞笑弹幕',
    tag: '搞笑',
    icon: require('../../Images/Persona/funny.png'),
    description: '快节奏剪辑，弹幕式文案与适当贴纸。',
    stylePreset: {
      tone: 'humorous',
      subtitle: {
        fontFamily: 'DIN Alternate',
        fontSize: 30,
        color: '#FFD700',
        position: 'top',
        animation: 'pop',
      },
      cut: {
        pace: 'fast',
        jumpCut: true,
        zoomPan: true,
      },
      transitions: 'flashy',
      overlay: {
        captions: true,
        stickers: true,
        barrage: true,
      },
      bgm: {
        mood: 'upbeat',
        volume: 0.5,
      },
    },
  },
  {
    id: 'builtin_romantic_lyrical',
    name: '抒情浪漫',
    tag: '温柔',
    icon: require('../../Images/Persona/romantic.png'),
    description: '温柔抒情，慢节奏与柔和转场，淡雅字幕。',
    stylePreset: {
      tone: 'romantic',
      subtitle: {
        fontFamily: 'Hiragino Sans',
        fontSize: 26,
        color: '#FFB6C1',
        position: 'bottom',
        animation: 'slide',
      },
      cut: {
        pace: 'slow',
        jumpCut: false,
        zoomPan: true,
      },
      transitions: 'smooth',
      overlay: {
        captions: true,
        stickers: false,
        barrage: false,
      },
      bgm: {
        mood: 'calm',
        volume: 0.35,
      },
    },
  },
  {
    id: 'builtin_sports_highlight',
    name: '激情体育',
    tag: '运动',
    icon: require('../../Images/Persona/gym.png'),
    description: '快速切片与节奏强烈的BGM，动感转场，强调关键瞬间。',
    stylePreset: {
      tone: 'humorous',
      subtitle: { fontFamily: 'DIN Alternate', fontSize: 28, color: '#FFFFFF', position: 'bottom', animation: 'bounce' },
      cut: { pace: 'fast', jumpCut: true, zoomPan: true },
      transitions: 'flashy',
      overlay: { captions: true, stickers: true, barrage: false },
      bgm: { mood: 'upbeat', volume: 0.55 },
    },
  },
  {
    id: 'builtin_tech_review',
    name: '科技测评',
    tag: '数码',
    icon: require('../../Images/Persona/tech.png'),
    description: '干净字幕与稳重转场，特写与参数点列展示。',
    stylePreset: {
      tone: 'rational',
      subtitle: { fontFamily: 'PingFang SC', fontSize: 26, color: '#00E5FF', position: 'bottom', animation: 'none' },
      cut: { pace: 'medium', jumpCut: true, zoomPan: false },
      transitions: 'smooth',
      overlay: { captions: true, stickers: false, barrage: false },
      bgm: { mood: 'cinematic', volume: 0.25 },
    },
  },
  {
    id: 'builtin_cinematic_trailer',
    name: '电影预告',
    tag: '大片',
    icon: require('../../Images/Persona/movie.png'),
    description: '电影化色调，强烈节奏，字幕居中大字号，戏剧化转场。',
    stylePreset: {
      tone: 'rational',
      subtitle: { fontFamily: 'Hiragino Sans', fontSize: 32, color: '#FFFFFF', position: 'center', animation: 'slide' },
      cut: { pace: 'fast', jumpCut: false, zoomPan: true },
      transitions: 'flashy',
      overlay: { captions: true, stickers: false, barrage: false },
      bgm: { mood: 'cinematic', volume: 0.4 },
    },
  },
  {
    id: 'builtin_vlog_minimal',
    name: '极简Vlog',
    tag: '生活',
    icon: require('../../Images/Persona/vlog.png'),
    description: '轻松舒缓，慢节奏，字幕小而简洁，过渡自然。',
    stylePreset: {
      tone: 'romantic',
      subtitle: { fontFamily: 'PingFang SC', fontSize: 22, color: '#E0E0E0', position: 'bottom', animation: 'none' },
      cut: { pace: 'slow', jumpCut: false, zoomPan: false },
      transitions: 'smooth',
      overlay: { captions: true, stickers: false, barrage: false },
      bgm: { mood: 'calm', volume: 0.25 },
    },
  },
  {
    id: 'builtin_gaming_montage',
    name: '游戏集锦',
    tag: '电竞',
    icon: require('../../Images/Persona/game.png'),
    description: '快速剪辑+弹幕风格文案，夸张贴纸，BGM强鼓点。',
    stylePreset: {
      tone: 'humorous',
      subtitle: { fontFamily: 'DIN Alternate', fontSize: 28, color: '#00FF88', position: 'top', animation: 'pop' },
      cut: { pace: 'fast', jumpCut: true, zoomPan: true },
      transitions: 'flashy',
      overlay: { captions: true, stickers: true, barrage: true },
      bgm: { mood: 'upbeat', volume: 0.6 },
    },
  },
  {
    id: 'builtin_news_fastcut',
    name: '新闻快剪',
    tag: '资讯',
    icon: require('../../Images/Persona/news.png'),
    description: '条理清晰、信息密度高，快节奏卡点，字幕规范对齐。',
    stylePreset: {
      tone: 'rational',
      subtitle: { fontFamily: 'PingFang SC', fontSize: 24, color: '#FFFFFF', position: 'bottom', animation: 'none' },
      cut: { pace: 'fast', jumpCut: true, zoomPan: false },
      transitions: 'smooth',
      overlay: { captions: true, stickers: false, barrage: false },
      bgm: { mood: 'cinematic', volume: 0.2 },
    },
  },
  {
    id: 'builtin_travel_montage',
    name: '旅行记录',
    tag: '风光',
    icon: require('../../Images/Persona/travel.png'),
    description: '自然过渡与轻快BGM，淡彩字幕，适度运镜。',
    stylePreset: {
      tone: 'romantic',
      subtitle: { fontFamily: 'Hiragino Sans', fontSize: 24, color: '#FFFFFF', position: 'bottom', animation: 'slide' },
      cut: { pace: 'medium', jumpCut: false, zoomPan: true },
      transitions: 'smooth',
      overlay: { captions: true, stickers: false, barrage: false },
      bgm: { mood: 'calm', volume: 0.35 },
    },
  },
];


