import AsyncStorage from '@react-native-async-storage/async-storage';
import { WorkspaceState } from './types';

const API_BASE_KEY = 'knowledge-base-studio.api-base';
const WORKSPACE_KEY = 'knowledge-base-studio.workspace';

export async function getApiBase(fallback: string): Promise<string> {
  return (await AsyncStorage.getItem(API_BASE_KEY)) || fallback;
}

export async function setApiBase(value: string): Promise<void> {
  await AsyncStorage.setItem(API_BASE_KEY, value);
}

export async function getWorkspace(): Promise<WorkspaceState | null> {
  const value = await AsyncStorage.getItem(WORKSPACE_KEY);
  return value ? JSON.parse(value) : null;
}

export async function setWorkspace(value: WorkspaceState): Promise<void> {
  await AsyncStorage.setItem(WORKSPACE_KEY, JSON.stringify(value));
}

export async function clearWorkspace(): Promise<void> {
  await AsyncStorage.removeItem(WORKSPACE_KEY);
}
