import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import jieba
import jieba.posseg as pseg
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedNLPParser:
    """增强的自然语言处理解析器，专门用于视频剪辑指令理解"""
    
    def __init__(self):
        self._init_jieba()
        self._init_operation_patterns()
        self._init_style_keywords()
        self._init_context_rules()
    
    def _init_jieba(self):
        """初始化jieba分词"""
        # 添加视频剪辑相关的专业词汇
        video_terms = [
            '剪辑', '裁剪', '转场', '特效', '滤镜', '调色', '字幕', '配乐',
            '快进', '慢放', '倒放', '循环', '拼接', '分割', '合并', '压缩',
            '高清', '标清', '4K', '1080P', '720P', '帧率', '码率', '分辨率',
            '特写', '远景', '中景', '全景', '推镜', '拉镜', '摇镜', '跟拍',
            '淡入', '淡出', '交叉', '溶解', '滑动', '缩放', '旋转', '翻转'
        ]
        
        for term in video_terms:
            jieba.add_word(term)
    
    def _init_operation_patterns(self):
        """初始化操作模式匹配"""
        self.operation_patterns = {
            'trim': {
                'keywords': ['剪', '裁', '缩短', '删除', '去掉', '移除'],
                'time_patterns': [
                    r'前(\d+)[秒分]',
                    r'后(\d+)[秒分]',
                    r'(\d+)[秒分]到(\d+)[秒分]',
                    r'从(\d+)[秒分]开始',
                    r'到(\d+)[秒分]结束'
                ],
                'description': '视频裁剪操作'
            },
            'speed': {
                'keywords': ['加速', '减速', '快', '慢', '倍速', '速度'],
                'speed_patterns': [
                    r'(\d+)倍速',
                    r'(\d+)倍快',
                    r'(\d+)倍慢',
                    r'加速(\d+)倍',
                    r'减速(\d+)倍'
                ],
                'description': '视频速度调整'
            },
            'transition': {
                'keywords': ['转场', '过渡', '切换', '淡入', '淡出', '交叉'],
                'transition_patterns': [
                    r'淡入淡出',
                    r'交叉溶解',
                    r'滑动转场',
                    r'缩放转场',
                    r'旋转转场'
                ],
                'description': '转场效果添加'
            },
            'text': {
                'keywords': ['文字', '字幕', '标题', '水印', '标注'],
                'text_patterns': [
                    r'添加文字[：:](.+)',
                    r'添加字幕[：:](.+)',
                    r'添加标题[：:](.+)'
                ],
                'description': '文字字幕添加'
            },
            'music': {
                'keywords': ['音乐', '背景音乐', '配乐', '音效', '音频'],
                'music_patterns': [
                    r'添加背景音乐',
                    r'添加配乐',
                    r'音乐音量(\d+)',
                    r'音频淡入(\d+)秒'
                ],
                'description': '音频处理'
            },
            'color': {
                'keywords': ['颜色', '调色', '滤镜', '亮度', '对比度', '饱和度'],
                'color_patterns': [
                    r'亮度(\d+)',
                    r'对比度(\d+)',
                    r'饱和度(\d+)',
                    r'暖色调',
                    r'冷色调',
                    r'黑白滤镜'
                ],
                'description': '颜色调整'
            },
            'effect': {
                'keywords': ['特效', '效果', '动画', '模糊', '锐化', '马赛克'],
                'effect_patterns': [
                    r'模糊效果',
                    r'锐化效果',
                    r'马赛克效果',
                    r'粒子特效',
                    r'光效'
                ],
                'description': '特效添加'
            }
        }
    
    def _init_style_keywords(self):
        """初始化风格关键词"""
        self.style_keywords = {
            'rhythm': {
                'fast': ['快节奏', '动感', '活力', '激情', '快速'],
                'slow': ['慢节奏', '舒缓', '平静', '温柔', '缓慢'],
                'dynamic': ['动态', '变化', '起伏', '波动'],
                'consistent': ['一致', '稳定', '均匀', '规律']
            },
            'visual': {
                'complex': ['复杂', '丰富', '多彩', '华丽'],
                'simple': ['简洁', '简约', '干净', '清爽'],
                'bright': ['明亮', '鲜艳', '高亮'],
                'dark': ['暗沉', '低调', '深沉']
            },
            'emotion': {
                'happy': ['快乐', '开心', '愉悦', '欢快'],
                'sad': ['悲伤', '忧郁', '伤感'],
                'energetic': ['充满活力', '精力充沛'],
                'calm': ['平静', '安宁', '祥和']
            }
        }
    
    def _init_context_rules(self):
        """初始化上下文规则"""
        self.context_rules = {
            'priority_operations': ['trim', 'speed', 'transition'],
            'dependent_operations': {
                'text': ['trim'],  # 添加文字通常需要先确定时间范围
                'music': ['trim'],  # 添加音乐通常需要先确定时间范围
                'effect': ['trim']  # 添加特效通常需要先确定时间范围
            },
            'conflict_operations': {
                'speed': ['speed'],  # 多次速度调整会冲突
                'trim': ['trim']     # 多次裁剪会冲突
            }
        }
    
    def parse_instruction(self, instruction: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """解析用户指令"""
        logger.info(f"解析指令: {instruction}")
        
        # 分词和词性标注
        words = list(pseg.cut(instruction))
        
        # 提取操作意图
        operations = self._extract_operations(instruction, words)
        
        # 提取风格偏好
        style_preferences = self._extract_style_preferences(instruction, words)
        
        # 提取时间信息
        time_info = self._extract_time_info(instruction)
        
        # 提取目标对象
        target_objects = self._extract_target_objects(instruction, words)
        
        # 分析指令复杂度
        complexity = self._analyze_complexity(instruction, operations)
        
        # 生成结构化结果
        result = {
            'original_instruction': instruction,
            'operations': operations,
            'style_preferences': style_preferences,
            'time_info': time_info,
            'target_objects': target_objects,
            'complexity': complexity,
            'confidence_score': self._calculate_confidence(operations, style_preferences),
            'parsed_at': datetime.now().isoformat()
        }
        
        # 应用上下文规则
        if context:
            result = self._apply_context_rules(result, context)
        
        logger.info(f"解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    
    def _extract_operations(self, instruction: str, words: List) -> List[Dict[str, Any]]:
        """提取操作信息"""
        operations = []
        
        for op_type, patterns in self.operation_patterns.items():
            # 检查关键词匹配
            if any(keyword in instruction for keyword in patterns['keywords']):
                operation = {
                    'type': op_type,
                    'description': patterns['description'],
                    'confidence': 0.8,
                    'params': {},
                    'patterns_matched': []
                }
                
                # 匹配具体参数模式
                for pattern in patterns.get('speed_patterns', []):
                    matches = re.findall(pattern, instruction)
                    if matches:
                        operation['patterns_matched'].append(pattern)
                        if op_type == 'speed':
                            operation['params']['factor'] = float(matches[0])
                
                for pattern in patterns.get('time_patterns', []):
                    matches = re.findall(pattern, instruction)
                    if matches:
                        operation['patterns_matched'].append(pattern)
                        if op_type == 'trim':
                            if len(matches[0]) == 2:  # 时间范围
                                operation['params']['start'] = float(matches[0][0])
                                operation['params']['end'] = float(matches[0][1])
                            else:  # 单个时间点
                                operation['params']['start'] = float(matches[0])
                
                for pattern in patterns.get('text_patterns', []):
                    matches = re.findall(pattern, instruction)
                    if matches:
                        operation['patterns_matched'].append(pattern)
                        operation['params']['text'] = matches[0]
                
                for pattern in patterns.get('transition_patterns', []):
                    if pattern in instruction:
                        operation['patterns_matched'].append(pattern)
                        operation['params']['type'] = pattern
                
                for pattern in patterns.get('color_patterns', []):
                    matches = re.findall(pattern, instruction)
                    if matches:
                        operation['patterns_matched'].append(pattern)
                        operation['params']['value'] = float(matches[0])
                
                for pattern in patterns.get('music_patterns', []):
                    if pattern in instruction:
                        operation['patterns_matched'].append(pattern)
                        operation['params']['action'] = pattern
                
                for pattern in patterns.get('effect_patterns', []):
                    if pattern in instruction:
                        operation['patterns_matched'].append(pattern)
                        operation['params']['effect'] = pattern
                
                operations.append(operation)
        
        return operations
    
    def _extract_style_preferences(self, instruction: str, words: List) -> Dict[str, float]:
        """提取风格偏好"""
        preferences = {}
        
        for category, styles in self.style_keywords.items():
            for style_name, keywords in styles.items():
                if any(keyword in instruction for keyword in keywords):
                    preferences[f"{category}_{style_name}"] = 0.8
        
        return preferences
    
    def _extract_time_info(self, instruction: str) -> Dict[str, Any]:
        """提取时间信息"""
        time_info = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'time_unit': 'seconds'
        }
        
        # 匹配时间模式
        time_patterns = [
            r'(\d+)[秒分]到(\d+)[秒分]',
            r'从(\d+)[秒分]开始',
            r'到(\d+)[秒分]结束',
            r'(\d+)[秒分]长',
            r'持续(\d+)[秒分]'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, instruction)
            if matches:
                if len(matches[0]) == 2:  # 时间范围
                    time_info['start_time'] = float(matches[0][0])
                    time_info['end_time'] = float(matches[0][1])
                    time_info['duration'] = time_info['end_time'] - time_info['start_time']
                else:  # 单个时间
                    time_info['duration'] = float(matches[0])
                break
        
        return time_info
    
    def _extract_target_objects(self, instruction: str, words: List) -> List[str]:
        """提取目标对象"""
        objects = []
        
        # 基于词性标注提取名词
        for word, flag in words:
            if flag.startswith('n'):  # 名词
                if word in ['人', '人物', '物体', '物品', '背景', '前景']:
                    objects.append(word)
        
        # 基于关键词匹配
        object_keywords = {
            'person': ['人', '人物', '脸', '身体'],
            'object': ['物体', '物品', '东西', '物品'],
            'background': ['背景', '环境', '场景'],
            'foreground': ['前景', '主体']
        }
        
        for obj_type, keywords in object_keywords.items():
            if any(keyword in instruction for keyword in keywords):
                objects.append(obj_type)
        
        return list(set(objects))
    
    def _analyze_complexity(self, instruction: str, operations: List[Dict]) -> str:
        """分析指令复杂度"""
        if len(operations) == 0:
            return 'simple'
        elif len(operations) == 1:
            return 'basic'
        elif len(operations) <= 3:
            return 'moderate'
        else:
            return 'complex'
    
    def _calculate_confidence(self, operations: List[Dict], style_preferences: Dict) -> float:
        """计算解析置信度"""
        if not operations and not style_preferences:
            return 0.3
        
        confidence = 0.5
        
        # 基于操作数量调整
        if len(operations) > 0:
            confidence += 0.2
        
        # 基于模式匹配数量调整
        total_patterns = sum(len(op.get('patterns_matched', [])) for op in operations)
        if total_patterns > 0:
            confidence += min(0.3, total_patterns * 0.1)
        
        # 基于风格偏好调整
        if style_preferences:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _apply_context_rules(self, result: Dict, context: Dict) -> Dict:
        """应用上下文规则"""
        # 处理依赖关系
        for op in result['operations']:
            if op['type'] in self.context_rules['dependent_operations']:
                dependencies = self.context_rules['dependent_operations'][op['type']]
                if not any(dep in [existing_op['type'] for existing_op in result['operations']] for dep in dependencies):
                    op['requires_dependency'] = dependencies
        
        # 处理冲突关系
        operation_types = [op['type'] for op in result['operations']]
        for op_type in operation_types:
            if op_type in self.context_rules['conflict_operations']:
                conflicts = self.context_rules['conflict_operations'][op_type]
                conflict_count = sum(1 for t in operation_types if t in conflicts)
                if conflict_count > 1:
                    result['warnings'] = result.get('warnings', [])
                    result['warnings'].append(f"检测到{op_type}操作的潜在冲突")
        
        return result
    
    def generate_editing_plan(self, parsed_instruction: Dict, persona_style: Dict = None) -> Dict[str, Any]:
        """根据解析结果生成剪辑方案"""
        plan = {
            'operations': [],
            'estimated_duration': 0,
            'style_notes': [],
            'confidence_score': parsed_instruction['confidence_score'],
            'warnings': parsed_instruction.get('warnings', [])
        }
        
        # 转换操作格式
        for op in parsed_instruction['operations']:
            plan_op = {
                'type': op['type'],
                'params': op['params'],
                'description': op['description'],
                'confidence': op['confidence']
            }
            
            # 应用人格风格
            if persona_style:
                plan_op = self._apply_persona_style(plan_op, persona_style)
            
            plan['operations'].append(plan_op)
        
        # 添加风格说明
        if persona_style:
            plan['style_notes'].append("应用用户个性化剪辑风格")
        
        if parsed_instruction['style_preferences']:
            plan['style_notes'].append("应用指令中的风格偏好")
        
        return plan
    
    def _apply_persona_style(self, operation: Dict, persona_style: Dict) -> Dict:
        """应用人格风格到操作"""
        # 根据人格风格调整操作参数
        if operation['type'] == 'speed' and 'factor' in operation['params']:
            if persona_style.get('fast_paced', 0) > 0.7:
                operation['params']['factor'] = max(operation['params']['factor'], 1.5)
            elif persona_style.get('slow_paced', 0) > 0.7:
                operation['params']['factor'] = min(operation['params']['factor'], 0.8)
        
        elif operation['type'] == 'transition':
            if persona_style.get('transition_smoothness', 0) > 0.7:
                operation['params']['duration'] = operation['params'].get('duration', 1.0) * 1.5
        
        return operation
    
    def validate_instruction(self, instruction: str) -> Dict[str, Any]:
        """验证指令的有效性"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 检查指令长度
        if len(instruction.strip()) < 3:
            validation_result['is_valid'] = False
            validation_result['errors'].append("指令太短，请提供更详细的描述")
        
        # 检查是否包含操作关键词
        has_operation = any(
            any(keyword in instruction for keyword in patterns['keywords'])
            for patterns in self.operation_patterns.values()
        )
        
        if not has_operation:
            validation_result['warnings'].append("未检测到明确的剪辑操作，建议使用更具体的指令")
            validation_result['suggestions'].append("例如：'剪掉前10秒'、'加速2倍'、'添加淡入淡出转场'")
        
        # 检查时间表达
        time_patterns = [r'\d+[秒分]', r'\d+到\d+']
        has_time = any(re.search(pattern, instruction) for pattern in time_patterns)
        
        if not has_time and any(op in instruction for op in ['剪', '裁', '速度']):
            validation_result['suggestions'].append("建议指定具体的时间参数，如'前10秒'、'2倍速'")
        
        return validation_result
