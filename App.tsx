import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import MediaPickerScreen from './App/MediaPickerScreen';
import EditMediaScreen from './App/EditMediaScreen';

const Stack = createStackNavigator();

const App: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="MediaPicker">
        <Stack.Screen name="MediaPicker" component={MediaPickerScreen} options={{ title: '选择媒体' }} />
        <Stack.Screen name="EditMedia" component={EditMediaScreen} options={{ title: '编辑媒体' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;