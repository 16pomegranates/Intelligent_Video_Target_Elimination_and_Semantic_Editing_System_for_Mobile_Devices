import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { builtInPresets, buildInstructionFromPreset } from '../utils/personaPresets';
import { PersonaManager, Persona } from '../utils/personaManager';

type ActivePersonaSource = 'builtin' | 'user';

export interface ActivePersonaState {
  id: string;
  name: string;
  source: ActivePersonaSource;
  instruction: string;
}

interface PersonaContextValue {
  activePersona: ActivePersonaState | null;
  applyPreset: (presetId: string) => Promise<ActivePersonaState | null>;
  applyUserPersona: (personaId: string) => Promise<ActivePersonaState | null>;
  clearActivePersona: () => Promise<void>;
}

const ACTIVE_PERSONA_KEY = '@active_persona';

const PersonaContext = createContext<PersonaContextValue | undefined>(undefined);

export const PersonaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePersona, setActivePersona] = useState<ActivePersonaState | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(ACTIVE_PERSONA_KEY);
        if (raw) {
          const parsed = JSON.parse(raw) as ActivePersonaState;
          setActivePersona(parsed);
        }
      } catch (e) {
        // noop
      }
    })();
  }, []);

  const persist = async (state: ActivePersonaState | null) => {
    if (!state) {
      await AsyncStorage.removeItem(ACTIVE_PERSONA_KEY);
      return;
    }
    await AsyncStorage.setItem(ACTIVE_PERSONA_KEY, JSON.stringify(state));
  };

  const applyPreset = async (presetId: string): Promise<ActivePersonaState | null> => {
    const preset = builtInPresets.find(p => p.id === presetId);
    if (!preset) return null;
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    const next: ActivePersonaState = {
      id: preset.id,
      name: preset.name,
      source: 'builtin',
      instruction,
    };
    setActivePersona(next);
    await persist(next);
    return next;
  };

  const applyUserPersona = async (personaId: string): Promise<ActivePersonaState | null> => {
    const all: Persona[] = await PersonaManager.getAllPersonas();
    const match = all.find(p => p.id === personaId);
    if (!match) return null;
    const instruction = match.instruction || match.description || '';
    const next: ActivePersonaState = {
      id: match.id,
      name: match.name,
      source: 'user',
      instruction,
    };
    setActivePersona(next);
    await persist(next);
    return next;
  };

  const clearActivePersona = async () => {
    setActivePersona(null);
    await persist(null);
  };

  const value = useMemo<PersonaContextValue>(() => ({ activePersona, applyPreset, applyUserPersona, clearActivePersona }), [activePersona]);

  return <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>;
};

export const usePersona = (): PersonaContextValue => {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error('usePersona must be used within PersonaProvider');
  return ctx;
};


