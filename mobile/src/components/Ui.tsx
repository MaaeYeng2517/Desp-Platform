import React, { ReactNode } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export const colors = {
  background: '#08111f',
  panel: '#101d32',
  panelSoft: '#172842',
  border: 'rgba(148,170,205,0.18)',
  text: '#edf4ff',
  muted: '#8fa3bf',
  muted2: '#617491',
  accent: '#6ee7d8',
  accentSoft: 'rgba(110,231,216,0.12)',
  blue: '#6ea8fe',
  blueSoft: 'rgba(110,168,254,0.12)',
  violet: '#a78bfa',
  amber: '#fbbf63',
  red: '#fb7185',
  redSoft: 'rgba(251,113,133,0.12)',
};

interface ScreenProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function Screen({ children, title, subtitle, actions }: ScreenProps) {
  return (
    <SafeAreaView edges={['top', 'bottom']} style={styles.screen}>
      <View style={styles.header}>
        <View style={styles.headerCopy}>
          {title ? <Text style={styles.title}>{title}</Text> : null}
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        {actions ? <View style={styles.headerActions}>{actions}</View> : null}
      </View>
      <View style={styles.content}>{children}</View>
    </SafeAreaView>
  );
}

export function Section({ title, eyebrow, children, action }: { title: string; eyebrow?: string; children: ReactNode; action?: ReactNode }) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <View>
          {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
          <Text style={styles.sectionTitle}>{title}</Text>
        </View>
        {action}
      </View>
      {children}
    </View>
  );
}

export function Button({ children, onPress, variant = 'primary', disabled, style }: { children: ReactNode; onPress: () => void; variant?: 'primary' | 'secondary' | 'quiet' | 'danger'; disabled?: boolean; style?: object }) {
  const tone = variant === 'primary' ? styles.primaryButton : variant === 'secondary' ? styles.secondaryButton : variant === 'danger' ? styles.dangerButton : styles.quietButton;
  return (
    <Pressable disabled={disabled} onPress={onPress} style={({ pressed }) => [styles.button, tone, style, pressed && styles.pressed]}>
      <Text style={[styles.buttonText, variant === 'quiet' && styles.quietButtonText]}>{children}</Text>
    </Pressable>
  );
}

export function Input({ value, onChangeText, placeholder, multiline, secureTextEntry, keyboardType, autoCapitalize, testID }: { value: string; onChangeText: (value: string) => void; placeholder?: string; multiline?: boolean; secureTextEntry?: boolean; keyboardType?: 'default' | 'email-address' | 'numeric' | 'url'; autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters'; testID?: string }) {
  return (
    <TextInput
      autoCapitalize={autoCapitalize}
      keyboardType={keyboardType}
      multiline={multiline}
      onChangeText={onChangeText}
      placeholder={placeholder}
      placeholderTextColor={colors.muted2}
      secureTextEntry={secureTextEntry}
      style={[styles.input, multiline && styles.multilineInput]}
      testID={testID}
      value={value}
    />
  );
}

export function Pill({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'running' }) {
  const style = tone === 'success' ? styles.successPill : tone === 'warning' ? styles.warningPill : tone === 'danger' ? styles.dangerPill : tone === 'running' ? styles.runningPill : styles.neutralPill;
  return <Text style={[styles.pill, style]}>{children}</Text>;
}

export function Loading({ label = 'Loading' }: { label?: string }) {
  return (
    <View style={styles.loading}>
      <ActivityIndicator color={colors.accent} />
      <Text style={styles.loadingText}>{label}</Text>
    </View>
  );
}

export function ErrorText({ children }: { children: string }) {
  return <Text style={styles.errorText}>{children}</Text>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: { alignItems: 'flex-start', flexDirection: 'row', gap: 12, justifyContent: 'space-between', padding: 20, paddingBottom: 14 },
  headerCopy: { flex: 1, gap: 4 },
  headerActions: { flexDirection: 'row', gap: 8 },
  title: { color: colors.text, fontSize: 24, fontWeight: '800', letterSpacing: -0.03, lineHeight: 29 },
  subtitle: { color: colors.muted, fontSize: 13, lineHeight: 18 },
  content: { flex: 1, paddingHorizontal: 16, paddingBottom: 24 },
  section: { backgroundColor: colors.panel, borderColor: colors.border, borderRadius: 16, borderWidth: 1, marginBottom: 14, padding: 14 },
  sectionHeader: { alignItems: 'flex-start', flexDirection: 'row', gap: 10, justifyContent: 'space-between', marginBottom: 12 },
  eyebrow: { color: colors.accent, fontSize: 10, fontWeight: '800', letterSpacing: 1.2, textTransform: 'uppercase' },
  sectionTitle: { color: colors.text, fontSize: 16, fontWeight: '750', marginTop: 4 },
  button: { alignItems: 'center', borderRadius: 10, justifyContent: 'center', minHeight: 40, paddingHorizontal: 13 },
  pressed: { opacity: 0.72 },
  primaryButton: { backgroundColor: colors.accent },
  secondaryButton: { backgroundColor: colors.blueSoft, borderColor: 'rgba(110,168,254,0.3)', borderWidth: 1 },
  quietButton: { backgroundColor: 'rgba(148,170,205,0.08)', borderColor: colors.border, borderWidth: 1 },
  dangerButton: { backgroundColor: colors.redSoft, borderColor: 'rgba(251,113,133,0.3)', borderWidth: 1 },
  buttonText: { color: '#06151d', fontSize: 12, fontWeight: '800' },
  quietButtonText: { color: colors.text },
  input: { backgroundColor: '#050d19', borderColor: colors.border, borderRadius: 9, color: colors.text, fontSize: 13, minHeight: 42, paddingHorizontal: 11, width: '100%' },
  multilineInput: { minHeight: 110, paddingTop: 10, textAlignVertical: 'top' },
  pill: { borderRadius: 20, fontSize: 10, fontWeight: '800', overflow: 'hidden', paddingHorizontal: 9, paddingVertical: 5, textAlign: 'center' },
  neutralPill: { backgroundColor: 'rgba(148,170,205,0.1)', color: colors.muted },
  successPill: { backgroundColor: colors.accentSoft, color: colors.accent },
  warningPill: { backgroundColor: 'rgba(251,191,99,0.12)', color: colors.amber },
  dangerPill: { backgroundColor: colors.redSoft, color: colors.red },
  runningPill: { backgroundColor: colors.blueSoft, color: colors.blue },
  loading: { alignItems: 'center', gap: 8, justifyContent: 'center', padding: 28 },
  loadingText: { color: colors.muted, fontSize: 12 },
  errorText: { color: colors.red, fontSize: 12, lineHeight: 17, marginTop: 8 },
});
