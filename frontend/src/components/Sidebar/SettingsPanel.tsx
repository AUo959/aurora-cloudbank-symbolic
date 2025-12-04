import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PlaygroundLanguage, PlaygroundTheme } from '@/types/playground';
import { Moon, SunMedium, Code2, TextCursorInput } from 'lucide-react';

interface SettingsPanelProps {
  language: PlaygroundLanguage;
  theme: PlaygroundTheme;
  fontSize: number;
  onLanguageChange: (language: PlaygroundLanguage) => void;
  onThemeChange: (theme: PlaygroundTheme) => void;
  onFontSizeChange: (size: number) => void;
}

export function SettingsPanel({
  language,
  theme,
  fontSize,
  onLanguageChange,
  onThemeChange,
  onFontSizeChange,
}: SettingsPanelProps) {
  return (
    <Card className="bg-black/40 text-white">
      <CardHeader className="flex items-center gap-2">
        <Code2 className="h-5 w-5 text-primary-400" aria-hidden />
        <CardTitle className="text-lg">Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm text-gray-400">Language</p>
          <div role="group" aria-label="Language selection" className="flex gap-2">
            <Button
              variant={language === 'python' ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => onLanguageChange('python')}
              aria-pressed={language === 'python' ? 'true' : 'false'}
            >
              Python
            </Button>
            <Button
              variant={language === 'javascript' ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => onLanguageChange('javascript')}
              aria-pressed={language === 'javascript' ? 'true' : 'false'}
            >
              JavaScript
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-gray-400">Theme</p>
          <div role="group" aria-label="Theme selection" className="flex gap-2">
            <Button
              variant={theme === 'dark' ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => onThemeChange('dark')}
              className="gap-2"
              aria-pressed={theme === 'dark' ? 'true' : 'false'}
            >
              <Moon className="h-4 w-4" /> Dark
            </Button>
            <Button
              variant={theme === 'light' ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => onThemeChange('light')}
              className="gap-2"
              aria-pressed={theme === 'light' ? 'true' : 'false'}
            >
              <SunMedium className="h-4 w-4" /> Light
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span className="flex items-center gap-2">
              <TextCursorInput className="h-4 w-4" /> Font size
            </span>
            <span className="text-primary-200">{fontSize}px</span>
          </div>
          <input
            aria-label="Font size"
            type="range"
            min={12}
            max={22}
            value={fontSize}
            onChange={(event) => onFontSizeChange(Number(event.target.value))}
            className="w-full accent-primary-400"
          />
        </div>
      </CardContent>
    </Card>
  );
}
