import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { useSpeechSynthesis, useSpeechRecognition } from "react-speech-kit";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import { Activity, Target, TrendingUp, Mic, MicOff, Volume2, VolumeX, Square, Trophy, Users, Music, Bell, Coins, Gift, Zap, Crown, Star, Flame } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Assessment Component
const AssessmentForm = ({ onAssessmentCreated }) => {
  const [formData, setFormData] = useState({
    player_name: "",
    age: "",
    position: "",
    sprint_40m: "",
    sprint_100m: "",
    cone_drill: "",
    ladder_drill: "",
    shuttle_run: "",
    sit_reach: "",
    shoulder_flexibility: "",
    hip_flexibility: "",
    juggling_count: "",
    dribbling_time: "",
    passing_accuracy: "",
    shooting_accuracy: ""
  });

  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/assessments`, formData);
      onAssessmentCreated(response.data);
      setFormData({
        player_name: "",
        age: "",
        position: "",
        sprint_40m: "",
        sprint_100m: "",
        cone_drill: "",
        ladder_drill: "",
        shuttle_run: "",
        sit_reach: "",
        shoulder_flexibility: "",
        hip_flexibility: "",
        juggling_count: "",
        dribbling_time: "",
        passing_accuracy: "",
        shooting_accuracy: ""
      });
    } catch (error) {
      console.error("خطأ في إنشاء التقييم:", error);
    }
    setIsLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Card className="max-w-4xl mx-auto bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50 border-orange-300 fire-glow">
      <CardHeader className="text-center">
        <CardTitle className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent">
          🔥 تقييم يويو الفتى الناري 🔥
        </CardTitle>
        <CardDescription className="text-orange-700 text-lg font-semibold">
          ✨ اكتشف قوتك الحقيقية وأشعل النار في الملعب! ✨
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="player_name" className="text-orange-800 font-bold flex items-center">
                <Fire className="ml-2 w-4 h-4" />
                اسم المحارب الناري
              </Label>
              <Input
                id="player_name"
                name="player_name"
                value={formData.player_name}
                onChange={handleChange}
                required
                className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100"
                dir="rtl"
                placeholder="أدخل اسمك يا بطل!"
              />
            </div>
            <div>
              <Label htmlFor="age" className="text-orange-800 font-bold flex items-center">
                <Star className="ml-2 w-4 h-4" />
                عمر النجم
              </Label>
              <Input
                id="age"
                name="age"
                type="number"
                value={formData.age}
                onChange={handleChange}
                required
                className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100"
                placeholder="كم عمرك؟"
              />
            </div>
            <div>
              <Label htmlFor="position" className="text-orange-800 font-bold flex items-center">
                <Target className="ml-2 w-4 h-4" />
                مركز القوة
              </Label>
              <Select onValueChange={(value) => setFormData({...formData, position: value})}>
                <SelectTrigger className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100">
                  <SelectValue placeholder="اختر مركزك في المعركة" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="goalkeeper">🥅 حارس الحصن</SelectItem>
                  <SelectItem value="defender">🛡️ محارب الدفاع</SelectItem>
                  <SelectItem value="midfielder">⚡ سيد الوسط</SelectItem>
                  <SelectItem value="forward">🗡️ مهاجم ناري</SelectItem>
                  <SelectItem value="striker">🔥 مدمر الشباك</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Speed Metrics */}
          <div className="bg-gradient-to-r from-red-100 to-orange-100 rounded-lg p-6 border-2 border-red-300 fire-glow">
            <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center">
              <Zap className="ml-2 text-yellow-500" />
              قوة السرعة الخارقة ⚡
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="sprint_40m" className="text-red-700 font-semibold">🏃‍♂️ عدو 40 متر (ثانية)</Label>
                <Input
                  id="sprint_40m"
                  name="sprint_40m"
                  type="number"
                  step="0.01"
                  value={formData.sprint_40m}
                  onChange={handleChange}
                  required
                  className="border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50"
                  placeholder="سرعة البرق!"
                />
              </div>
              <div>
                <Label htmlFor="sprint_100m" className="text-red-700 font-semibold">🚀 عدو 100 متر (ثانية)</Label>
                <Input
                  id="sprint_100m"
                  name="sprint_100m"
                  type="number"
                  step="0.01"
                  value={formData.sprint_100m}
                  onChange={handleChange}
                  required
                  className="border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50"
                  placeholder="أسرع من الريح!"
                />
              </div>
            </div>
          </div>

          {/* Agility Metrics */}
          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-6 border-2 border-yellow-400 fire-glow">
            <h3 className="text-xl font-bold text-yellow-800 mb-4 flex items-center">
              <Target className="ml-2 text-orange-500" />
              مهارات الرشاقة الذهبية 🎯
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="cone_drill" className="text-yellow-700 font-semibold">🔶 تدريب المخاريط (ثانية)</Label>
                <Input
                  id="cone_drill"
                  name="cone_drill"
                  type="number"
                  step="0.01"
                  value={formData.cone_drill}
                  onChange={handleChange}
                  required
                  className="border-yellow-400 focus:border-orange-500 bg-gradient-to-r from-yellow-50 to-orange-50"
                />
              </div>
              <div>
                <Label htmlFor="ladder_drill" className="text-yellow-700 font-semibold">🪜 تدريب السلم (ثانية)</Label>
                <Input
                  id="ladder_drill"
                  name="ladder_drill"
                  type="number"
                  step="0.01"
                  value={formData.ladder_drill}
                  onChange={handleChange}
                  required
                  className="border-yellow-400 focus:border-orange-500 bg-gradient-to-r from-yellow-50 to-orange-50"
                />
              </div>
              <div>
                <Label htmlFor="shuttle_run" className="text-yellow-700 font-semibold">🔄 الجري المكوكي (ثانية)</Label>
                <Input
                  id="shuttle_run"
                  name="shuttle_run"
                  type="number"
                  step="0.01"
                  value={formData.shuttle_run}
                  onChange={handleChange}
                  required
                  className="border-yellow-400 focus:border-orange-500 bg-gradient-to-r from-yellow-50 to-orange-50"
                />
              </div>
            </div>
          </div>

          {/* Flexibility Metrics */}
          <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-lg p-6 border-2 border-green-400 fire-glow">
            <h3 className="text-xl font-bold text-green-800 mb-4 flex items-center">
              🧘‍♂️ قوة المرونة السحرية
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="sit_reach" className="text-green-700 font-semibold">🤸‍♂️ الجلوس والوصول (سم)</Label>
                <Input
                  id="sit_reach"
                  name="sit_reach"
                  type="number"
                  step="0.1"
                  value={formData.sit_reach}
                  onChange={handleChange}
                  required
                  className="border-green-400 focus:border-blue-500 bg-gradient-to-r from-green-50 to-blue-50"
                />
              </div>
              <div>
                <Label htmlFor="shoulder_flexibility" className="text-green-700 font-semibold">💪 مرونة الكتف (درجة)</Label>
                <Input
                  id="shoulder_flexibility"
                  name="shoulder_flexibility"
                  type="number"
                  value={formData.shoulder_flexibility}
                  onChange={handleChange}
                  required
                  className="border-green-400 focus:border-blue-500 bg-gradient-to-r from-green-50 to-blue-50"
                />
              </div>
              <div>
                <Label htmlFor="hip_flexibility" className="text-green-700 font-semibold">🦵 مرونة الورك (درجة)</Label>
                <Input
                  id="hip_flexibility"  
                  name="hip_flexibility"
                  type="number"
                  value={formData.hip_flexibility}
                  onChange={handleChange}
                  required
                  className="border-green-400 focus:border-blue-500 bg-gradient-to-r from-green-50 to-blue-50"
                />
              </div>
            </div>
          </div>

          {/* Ball Handling Metrics */}
          <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-6 border-2 border-purple-400 fire-glow">
            <h3 className="text-xl font-bold text-purple-800 mb-4 flex items-center">
              ⚽ سحر التحكم بالكرة ✨
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="juggling_count" className="text-purple-700 font-semibold">🤹‍♂️ عدد الشقلبات السحرية</Label>
                <Input
                  id="juggling_count"
                  name="juggling_count"
                  type="number"
                  value={formData.juggling_count}
                  onChange={handleChange}
                  required
                  className="border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50"
                />
              </div>
              <div>
                <Label htmlFor="dribbling_time" className="text-purple-700 font-semibold">🏃‍♂️ وقت المراوغة الساحرة (ثانية)</Label>
                <Input
                  id="dribbling_time"
                  name="dribbling_time"
                  type="number"
                  step="0.01"
                  value={formData.dribbling_time}
                  onChange={handleChange}
                  required
                  className="border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50"
                />
              </div>
              <div>
                <Label htmlFor="passing_accuracy" className="text-purple-700 font-semibold">🎯 دقة التمرير (%)</Label>
                <Input
                  id="passing_accuracy"
                  name="passing_accuracy"
                  type="number"
                  step="0.1"
                  value={formData.passing_accuracy}
                  onChange={handleChange}
                  required
                  className="border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50"
                />
              </div>
              <div>
                <Label htmlFor="shooting_accuracy" className="text-purple-700 font-semibold">⚽ دقة التسديد القاتلة (%)</Label>
                <Input
                  id="shooting_accuracy"
                  name="shooting_accuracy"
                  type="number"
                  step="0.1"
                  value={formData.shooting_accuracy}
                  onChange={handleChange}
                  required
                  className="border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50"
                />
              </div>
            </div>
          </div>

          <Button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 hover:from-orange-700 hover:via-red-700 hover:to-yellow-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 fire-glow text-xl"
          >
            {isLoading ? "🔥 جاري إنشاء ملف يويو الناري..." : "🚀 أشعل النار وابدأ رحلة المجد! 🚀"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

// Training Program Component
const TrainingProgram = ({ playerId, playerName }) => {
  const [programs, setPrograms] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [spotifyLink, setSpotifyLink] = useState("");
  const [isGroup, setIsGroup] = useState(false);
  const { speak, cancel, speaking, voices } = useSpeechSynthesis();

  useEffect(() => {
    fetchPrograms();
  }, [playerId]);

  const fetchPrograms = async () => {
    try {
      const response = await axios.get(`${API}/training-programs/${playerId}`);
      setPrograms(response.data);
    } catch (error) {
      console.error("خطأ في جلب البرامج:", error);
    }
  };

  const generateProgram = async (programType) => {
    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/training-programs`, {
        player_id: playerId,
        program_type: programType,
        is_group: isGroup,
        spotify_playlist: spotifyLink || null
      });
      setPrograms([response.data, ...programs]);
      setSpotifyLink("");
    } catch (error) {
      console.error("خطأ في إنشاء البرنامج:", error);
    }
    setIsGenerating(false);
  };

  const speakProgram = (content) => {
    if (speaking) {
      cancel();
    } else {
      const arabicVoice = voices.find(voice => voice.lang.includes('ar')) || voices[0];
      speak({ 
        text: content, 
        voice: arabicVoice,
        rate: 0.8,
        pitch: 1
      });
    }
  };

  const stopSpeaking = () => {
    cancel();
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-4">
          🔥 برامج التدريب الناري ليويو {playerName} 🔥
        </h2>
        
        {/* Options */}
        <div className="bg-gradient-to-r from-orange-100 to-red-100 p-4 rounded-lg mb-4 border-2 border-orange-300">
          <div className="flex flex-col space-y-4">
            <div className="flex items-center justify-center space-x-4">
              <Label className="flex items-center space-x-2 ml-4">
                <input
                  type="checkbox"
                  checked={isGroup}
                  onChange={(e) => setIsGroup(e.target.checked)}
                  className="form-checkbox text-orange-600"
                />
                <Users className="w-4 h-4 text-orange-600 ml-2" />
                <span className="text-orange-800 font-semibold">تدريب جماعي مع الأصدقاء</span>
              </Label>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <Music className="w-5 h-5 text-green-600" />
              <Input
                placeholder="رابط Spotify للتحفيز (اختياري)"
                value={spotifyLink}
                onChange={(e) => setSpotifyLink(e.target.value)}
                className="max-w-md border-green-400 focus:border-green-600"
                dir="rtl"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-center space-x-4">
          <Button
            onClick={() => generateProgram("AI_Generated")}
            disabled={isGenerating}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 fire-glow ml-4"
          >
            {isGenerating ? "🔥 جاري الإنشاء..." : "🤖 برنامج يويو الذكي الناري"}
          </Button>
          <Button
            onClick={() => generateProgram("Ronaldo_Template")}
            disabled={isGenerating}
            className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 fire-glow"
          >
            {isGenerating ? "🔥 جاري الإنشاء..." : "👑 قالب رونالدو الأسطوري"}
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        {programs.map((program) => (
          <Card key={program.id} className="bg-gradient-to-br from-white to-orange-50 border-2 border-orange-200 fire-glow">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-xl text-orange-800 flex items-center">
                    <Fire className="ml-2 w-5 h-5" />
                    برنامج {program.program_type === "AI_Generated" ? "الذكاء الاصطناعي الناري 🤖" : program.program_type === "Ronaldo_Template" ? "رونالدو الأسطوري 👑" : "مخصص 🔥"}
                  </CardTitle>
                  <CardDescription className="flex items-center space-x-2">
                    <span>تم إنشاؤه: {new Date(program.created_at).toLocaleDateString('ar-SA')}</span>
                    {program.is_group && <Badge className="bg-blue-100 text-blue-800 mr-2">تدريب جماعي 👥</Badge>}
                    {program.spotify_playlist && <Badge className="bg-green-100 text-green-800 mr-2">موسيقى تحفيزية 🎵</Badge>}
                  </CardDescription>
                </div>
                <div className="flex space-x-2">
                  <Badge 
                    variant={program.program_type === "AI_Generated" ? "default" : "secondary"}
                    className="bg-orange-100 text-orange-800 ml-2"
                  >
                    {program.program_type === "AI_Generated" ? "ذكاء اصطناعي 🤖" : program.program_type === "Ronaldo_Template" ? "رونالدو 👑" : "مخصص 🔥"}
                  </Badge>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => speakProgram(program.program_content)}
                    className="border-orange-300 text-orange-700 hover:bg-orange-50"
                  >
                    {speaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </Button>
                  {speaking && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={stopSpeaking}
                      className="border-red-300 text-red-700 hover:bg-red-50"
                    >
                      <Square className="w-4 h-4" />
                    </Button>
                  )}
                  {program.spotify_playlist && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(program.spotify_playlist, '_blank')}
                      className="border-green-300 text-green-700 hover:bg-green-50"
                    >
                      <Music className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="content" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="content">محتوى البرنامج الناري 🔥</TabsTrigger>
                  <TabsTrigger value="schedule">الجدول الأسبوعي المحفز ⚡</TabsTrigger>
                  <TabsTrigger value="milestones">معالم المجد 🏆</TabsTrigger>
                </TabsList>
                <TabsContent value="content" className="mt-4">
                  <div className="bg-gradient-to-r from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200 max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 text-right" dir="rtl">{program.program_content}</pre>
                  </div>
                </TabsContent>
                <TabsContent value="schedule" className="mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(program.weekly_schedule || {}).map(([day, activity]) => {
                      const arabicDays = {
                        'Monday': 'الإثنين',
                        'Tuesday': 'الثلاثاء', 
                        'Wednesday': 'الأربعاء',
                        'Thursday': 'الخميس',
                        'Friday': 'الجمعة',
                        'Saturday': 'السبت',
                        'Sunday': 'الأحد'
                      };
                      return (
                        <div key={day} className="bg-gradient-to-r from-yellow-50 to-orange-50 p-3 rounded-lg border border-yellow-200">
                          <div className="font-semibold text-orange-800 text-right flex items-center">
                            <Fire className="w-4 h-4 ml-2" />
                            {arabicDays[day] || day}
                          </div>
                          <div className="text-sm text-gray-600 text-right" dir="rtl">{activity}</div>
                        </div>
                      );
                    })}
                  </div>
                </TabsContent>
                <TabsContent value="milestones" className="mt-4">
                  <div className="space-y-3">
                    {program.milestones?.map((milestone, index) => (
                      <div key={index} className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200 flex justify-between items-center">
                        <div className="text-right">
                          <span className="font-semibold text-green-800 flex items-center">
                            <Trophy className="w-4 h-4 ml-2" />
                            الأسبوع {milestone.week}:
                          </span>
                          <span className="mr-2 text-gray-700" dir="rtl">{milestone.target}</span>
                          {milestone.coins && (
                            <Badge className="bg-yellow-100 text-yellow-800 mr-2">
                              <Coins className="w-3 h-3 ml-1" />
                              {milestone.coins} عملة
                            </Badge>
                          )}
                        </div>
                        <Badge variant="outline" className="border-green-300 text-green-700">
                          هدف ناري 🔥
                        </Badge>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Progress Tracker Component with Achievements
const ProgressTracker = ({ playerId, playerName }) => {
  const [progressData, setProgressData] = useState([]);
  const [trophies, setTrophies] = useState([]);
  const [newEntry, setNewEntry] = useState({
    metric_type: "",
    metric_name: "",
    value: ""
  });
  const [lastResult, setLastResult] = useState(null);

  useEffect(() => {
    fetchProgress();
    fetchTrophies();
  }, [playerId]);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API}/progress/${playerId}`);
      setProgressData(response.data);
    } catch (error) {
      console.error("خطأ في جلب التقدم:", error);
    }
  };

  const fetchTrophies = async () => {
    try {
      const response = await axios.get(`${API}/trophies/${playerId}`);
      setTrophies(response.data);
    } catch (error) {
      console.error("خطأ في جلب الكؤوس:", error);
    }
  };

  const addProgress = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/progress`, {
        player_id: playerId,
        ...newEntry
      });
      setNewEntry({ metric_type: "", metric_name: "", value: "" });
      setLastResult(response.data);
      fetchProgress();
      fetchTrophies();
    } catch (error) {
      console.error("خطأ في إضافة التقدم:", error);
    }
  };

  // Process data for charts
  const chartData = progressData.reduce((acc, entry) => {
    const date = new Date(entry.date).toLocaleDateString('ar-SA');
    const existingDate = acc.find(item => item.date === date);
    if (existingDate) {
      existingDate[entry.metric_name] = entry.value;
    } else {
      acc.push({
        date,
        [entry.metric_name]: entry.value
      });
    }
    return acc;
  }, []).reverse();

  // Radar chart data
  const latestData = progressData.reduce((acc, entry) => {
    acc[entry.metric_name] = entry.value;
    return acc;
  }, {});

  const radarData = Object.entries(latestData).map(([metric, value]) => ({
    metric,
    value,
    fullMark: 100
  }));

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-4">
          🏆 متتبع إنجازات يويو {playerName} 🏆
        </h2>
      </div>

      {/* Last Result Display */}
      {lastResult && (
        <Card className="bg-gradient-to-r from-green-100 to-blue-100 border-2 border-green-400 fire-glow">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center">
              <Gift className="ml-2 w-5 h-5" />
              {lastResult.message}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center space-x-4">
              <Badge className="bg-yellow-100 text-yellow-800 text-lg p-2 ml-4">
                <Coins className="w-4 h-4 ml-1" />
                +{lastResult.coins_earned} عملة ذهبية
              </Badge>
              {lastResult.trophies_unlocked && lastResult.trophies_unlocked.length > 0 && (
                <div className="flex space-x-2">
                  {lastResult.trophies_unlocked.map((trophy, index) => (
                    <Badge key={index} className="bg-purple-100 text-purple-800 text-lg p-2 mr-2">
                      <Trophy className="w-4 h-4 ml-1" />
                      {trophy.icon} {trophy.trophy_name}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trophies Display */}
      {trophies.length > 0 && (
        <Card className="bg-gradient-to-r from-yellow-100 to-orange-100 border-2 border-yellow-400">
          <CardHeader>
            <CardTitle className="text-yellow-800 flex items-center">
              <Crown className="ml-2 w-5 h-5" />
              🏆 كؤوس يويو الناري 🏆
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trophies.map((trophy) => (
                <div key={trophy.id} className="bg-gradient-to-r from-gold-100 to-yellow-100 p-4 rounded-lg border border-yellow-300 text-center">
                  <div className="text-4xl mb-2">{trophy.icon}</div>
                  <div className="font-bold text-yellow-800">{trophy.trophy_name}</div>
                  <div className="text-sm text-yellow-600 mt-1">{trophy.description}</div>
                  <Badge className="bg-yellow-200 text-yellow-800 mt-2">
                    <Coins className="w-3 h-3 ml-1" />
                    +{trophy.coins_reward}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Progress Entry */}
      <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-300">
        <CardHeader>
          <CardTitle className="text-orange-800 flex items-center">
            <Fire className="ml-2 w-5 h-5" />
            🚀 أضف إنجازك الجديد يا يويو! 🚀
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={addProgress} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <Label className="text-orange-700 font-semibold">نوع المقياس</Label>
              <Select onValueChange={(value) => setNewEntry({...newEntry, metric_type: value})}>
                <SelectTrigger className="border-orange-400 focus:border-red-500">
                  <SelectValue placeholder="اختر نوع التحدي" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="speed">⚡ السرعة الخارقة</SelectItem>
                  <SelectItem value="agility">🎯 الرشاقة الذهبية</SelectItem>
                  <SelectItem value="flexibility">🧘‍♂️ المرونة السحرية</SelectItem>
                  <SelectItem value="ball_handling">⚽ سحر التحكم بالكرة</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-orange-700 font-semibold">اسم المقياس</Label>
              <Input
                placeholder="مثال: عدو 40 متر الناري"
                value={newEntry.metric_name}
                onChange={(e) => setNewEntry({...newEntry, metric_name: e.target.value})}
                required
                dir="rtl"
                className="border-orange-400 focus:border-red-500"
              />
            </div>
            <div>
              <Label className="text-orange-700 font-semibold">القيمة المذهلة</Label>
              <Input
                type="number"
                step="0.01"
                placeholder="إنجازك"
                value={newEntry.value}
                onChange={(e) => setNewEntry({...newEntry, value: e.target.value})}
                required
                className="border-orange-400 focus:border-red-500"
              />
            </div>
            <Button type="submit" className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 fire-glow">
              🔥 سجل الإنجاز
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-2 border-blue-300">
          <CardHeader>
            <CardTitle className="text-blue-800 flex items-center">
              <TrendingUp className="ml-2" />
              🚀 رحلة التقدم عبر الزمن
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(latestData).map((metric, index) => (
                  <Line
                    key={metric}
                    type="monotone"
                    dataKey={metric}
                    stroke={`hsl(${index * 60}, 70%, 50%)`}
                    strokeWidth={3}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-2 border-purple-300">
          <CardHeader>
            <CardTitle className="text-purple-800">🌟 ملف القوة الحالي</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                <Radar
                  name="قوة يويو"
                  dataKey="value"
                  stroke="#f97316"
                  fill="#f97316"
                  fillOpacity={0.3}
                  strokeWidth={3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Enhanced Voice Notes Component
const VoiceNotes = ({ playerId, playerName }) => {
  const [notes, setNotes] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const { transcript, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();
  const { speak, cancel, speaking, voices } = useSpeechSynthesis();

  useEffect(() => {
    fetchNotes();
    fetchNotifications();
  }, [playerId]);

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API}/voice-notes/${playerId}`);
      setNotes(response.data);
    } catch (error) {
      console.error("خطأ في جلب الملاحظات:", error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API}/notifications/${playerId}`);
      setNotifications(response.data);
    } catch (error) {
      console.error("خطأ في جلب الإشعارات:", error);
    }
  };

  const saveNote = async () => {
    if (!transcript) return;
    
    try {
      await axios.post(`${API}/voice-notes`, {
        player_id: playerId,
        note_text: transcript
      });
      resetTranscript();
      fetchNotes();
    } catch (error) {
      console.error("خطأ في حفظ الملاحظة:", error);
    }
  };

  const createMotivationNotification = async () => {
    try {
      const motivationalMessages = [
        "🔥 يويو! حان وقت إشعال النار في التدريب!",
        "⚡ استيقظ يا محارب! الملعب ينتظر قوتك!",
        "🚀 اليوم هو يومك لتحطيم كل الأرقام القياسية!",
        "👑 أنت الأسطورة! اذهب وأظهر للعالم قوتك الحقيقية!"
      ];
      
      const randomMessage = motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];
      
      await axios.post(`${API}/notifications`, {
        player_id: playerId,
        title: "⏰ إشعار التحفيز الناري",
        message: randomMessage,
        notification_type: "motivation",
        spotify_link: "https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP" // Example workout playlist
      });
      
      fetchNotifications();
    } catch (error) {
      console.error("خطأ في إنشاء إشعار التحفيز:", error);
    }
  };

  const speakNote = (text) => {
    if (speaking) {
      cancel();
    } else {
      const arabicVoice = voices.find(voice => voice.lang.includes('ar')) || voices[0];
      speak({ 
        text: text, 
        voice: arabicVoice,
        rate: 0.8,
        pitch: 1
      });
    }
  };

  const stopSpeaking = () => {
    cancel();
  };

  if (!browserSupportsSpeechRecognition) {
    return <div className="text-center text-red-600">المتصفح لا يدعم التعرف على الكلام.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-4">
          🎤 مذكرات يويو الصوتية والإشعارات 🔔
        </h2>
      </div>

      {/* Notifications */}
      {notifications.length > 0 && (
        <Card className="bg-gradient-to-r from-blue-100 to-purple-100 border-2 border-blue-300">
          <CardHeader>
            <CardTitle className="text-blue-800 flex items-center">
              <Bell className="ml-2 w-5 h-5" />
              🔔 إشعارات التحفيز الناري
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-40 overflow-y-auto">
              {notifications.slice(0, 5).map((notification) => (
                <div key={notification.id} className="bg-white p-3 rounded-lg border border-blue-200 flex justify-between items-center">
                  <div className="text-right flex-1">
                    <div className="font-semibold text-blue-800">{notification.title}</div>
                    <div className="text-sm text-blue-600" dir="rtl">{notification.message}</div>
                    {notification.spotify_link && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(notification.spotify_link, '_blank')}
                        className="mt-2 border-green-300 text-green-700 hover:bg-green-50"
                      >
                        <Music className="w-3 h-3 ml-1" />
                        استمع للتحفيز
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Voice Input */}
      <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-300">
        <CardHeader>
          <CardTitle className="text-orange-800 flex items-center">
            <Fire className="ml-2 w-5 h-5" />
            🎤 سجل مذكراتك الناري
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => setIsListening(!isListening)}
              className={`${isListening ? 'bg-red-600 hover:bg-red-700' : 'bg-orange-600 hover:bg-orange-700'} transition-colors ml-4 fire-glow`}
            >
              {isListening ? <MicOff className="ml-2" /> : <Mic className="ml-2" />}
              {isListening ? '🔴 إيقاف التسجيل' : '🎤 بدء التسجيل الناري'}
            </Button>
            <Button
              onClick={saveNote}
              disabled={!transcript}
              className="bg-blue-600 hover:bg-blue-700 fire-glow"
            >
              💾 حفظ المذكرة
            </Button>
            <Button
              onClick={resetTranscript}
              variant="outline"
              className="border-gray-300"
            >
              🗑️ مسح
            </Button>
            <Button
              onClick={createMotivationNotification}
              className="bg-purple-600 hover:bg-purple-700 fire-glow"
            >
              🔔 إشعار تحفيزي
            </Button>
            {speaking && (
              <Button
                onClick={stopSpeaking}
                variant="outline"
                className="border-red-300 text-red-700 hover:bg-red-50"
              >
                <Square className="w-4 h-4 ml-2" />
                إيقاف الصوت
              </Button>
            )}
          </div>
          
          {transcript && (
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-orange-200">
              <p className="text-gray-700 text-right" dir="rtl">{transcript}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Notes List */}
      <div className="space-y-4">
        {notes.map((note) => (
          <Card key={note.id} className="bg-gradient-to-r from-white to-orange-50 border border-orange-200">
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-gray-700 mb-2 text-right" dir="rtl">{note.note_text}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(note.created_at).toLocaleString('ar-SA')}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => speakNote(note.note_text)}
                  className="mr-4 border-orange-300 text-orange-700 hover:bg-orange-50"
                >
                  {speaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Group Training Component
const GroupTraining = ({ playerId, playerName }) => {
  const [groups, setGroups] = useState([]);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroup, setNewGroup] = useState({
    training_name: "",
    description: "",
    invited_members: "",
    spotify_playlist: ""
  });

  useEffect(() => {
    fetchGroups();
  }, [playerId]);

  const fetchGroups = async () => {
    try {
      const response = await axios.get(`${API}/group-training/${playerId}`);
      setGroups(response.data);
    } catch (error) {
      console.error("خطأ في جلب المجموعات:", error);
    }
  };

  const createGroup = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/group-training`, {
        creator_id: playerId,
        training_name: newGroup.training_name,
        description: newGroup.description,
        invited_members: newGroup.invited_members.split(',').map(id => id.trim()),
        spotify_playlist: newGroup.spotify_playlist || null
      });
      
      setNewGroup({
        training_name: "",
        description: "",
        invited_members: "",
        spotify_playlist: ""
      });
      setShowCreateGroup(false);
      fetchGroups();
    } catch (error) {
      console.error("خطأ في إنشاء المجموعة:", error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-4">
          👥 تدريبات المجموعة الناري 👥
        </h2>
        <Button
          onClick={() => setShowCreateGroup(!showCreateGroup)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 fire-glow"
        >
          <Users className="ml-2 w-4 h-4" />
          إنشاء مجموعة تدريب جديدة
        </Button>
      </div>

      {/* Create Group Form */}
      {showCreateGroup && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300">
          <CardHeader>
            <CardTitle className="text-blue-800">🔥 إنشاء مجموعة تدريب ناري</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={createGroup} className="space-y-4">
              <div>
                <Label className="text-blue-700 font-semibold">اسم المجموعة الناري</Label>
                <Input
                  value={newGroup.training_name}
                  onChange={(e) => setNewGroup({...newGroup, training_name: e.target.value})}
                  required
                  placeholder="مثال: محاربو يويو النار"
                  className="border-blue-400 focus:border-purple-500"
                  dir="rtl"
                />
              </div>
              <div>
                <Label className="text-blue-700 font-semibold">وصف التحدي</Label>
                <Input
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  required
                  placeholder="وصف التدريب والأهداف"
                  className="border-blue-400 focus:border-purple-500"
                  dir="rtl"
                />
              </div>
              <div>
                <Label className="text-blue-700 font-semibold">معرفات الأصدقاء (مفصولة بفاصلة)</Label>
                <Input
                  value={newGroup.invited_members}
                  onChange={(e) => setNewGroup({...newGroup, invited_members: e.target.value})}
                  placeholder="ID1, ID2, ID3"
                  className="border-blue-400 focus:border-purple-500"
                />
              </div>
              <div>
                <Label className="text-blue-700 font-semibold">رابط Spotify للتحفيز (اختياري)</Label>
                <Input
                  value={newGroup.spotify_playlist}
                  onChange={(e) => setNewGroup({...newGroup, spotify_playlist: e.target.value})}
                  placeholder="https://open.spotify.com/playlist/..."
                  className="border-blue-400 focus:border-purple-500"
                />
              </div>
              <div className="flex space-x-2">
                <Button type="submit" className="bg-green-600 hover:bg-green-700 fire-glow mr-2">
                  🚀 إنشاء المجموعة
                </Button>
                <Button type="button" onClick={() => setShowCreateGroup(false)} variant="outline">
                  إلغاء
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Groups List */}
      <div className="grid gap-6">
        {groups.map((group) => (
          <Card key={group.id} className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300">
            <CardHeader>
              <CardTitle className="text-green-800 flex items-center">
                <Users className="ml-2 w-5 h-5" />
                {group.training_name}
              </CardTitle>
              <CardDescription>{group.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-4">
                  <Badge className="bg-blue-100 text-blue-800 ml-4">
                    👥 {group.members.length + 1} عضو
                  </Badge>
                  <Badge className="bg-purple-100 text-purple-800 ml-4">
                    📅 {new Date(group.created_at).toLocaleDateString('ar-SA')}
                  </Badge>
                  {group.spotify_playlist && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(group.spotify_playlist, '_blank')}
                      className="border-green-300 text-green-700 hover:bg-green-50"
                    >
                      <Music className="w-4 h-4 ml-1" />
                      استمع للموسيقى
                    </Button>
                  )}
                </div>
                {group.target_date && (
                  <div className="text-sm text-gray-600">
                    تاريخ الهدف: {new Date(group.target_date).toLocaleDateString('ar-SA')}
                  </div>
                )}
                <Badge className="bg-yellow-100 text-yellow-800">
                  <Coins className="w-3 h-3 ml-1" />
                  مكافأة الإنجاز: {group.completion_reward} عملة
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [assessments, setAssessments] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState("assessment");

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      const response = await axios.get(`${API}/assessments`);
      setAssessments(response.data);
    } catch (error) {
      console.error("خطأ في جلب التقييمات:", error);
    }
  };

  const handleAssessmentCreated = (assessment) => {
    setAssessments([assessment, ...assessments]);
    setSelectedPlayer(assessment);
    setActiveTab("training");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-100 via-red-50 via-yellow-50 to-white fire-background" dir="rtl">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-4 fire-glow">
            🔥 يويو الفتى الناري ⚽
          </h1>
          <p className="text-orange-700 text-xl font-bold">
            ✨ مولد برامج التدريب الاحترافية مع رؤى مدعومة بالذكاء الاصطناعي ✨
          </p>
          <div className="flex justify-center items-center space-x-4 mt-4">
            <Badge className="bg-yellow-100 text-yellow-800 text-lg p-2 ml-4">
              <Fire className="w-4 h-4 ml-1" />
              أشعل النار في قوتك
            </Badge>
            <Badge className="bg-blue-100 text-blue-800 text-lg p-2 ml-4">
              <Users className="w-4 h-4 ml-1" />
              تدرب مع الأصدقاء
            </Badge>
            <Badge className="bg-green-100 text-green-800 text-lg p-2">
              <Trophy className="w-4 h-4 ml-1" />
              اجمع الكؤوس والعملات
            </Badge>
          </div>
        </div>

        {/* Player Selection */}
        {assessments.length > 0 && (
          <Card className="mb-8 bg-gradient-to-r from-white to-orange-50 border-2 border-orange-300 fire-glow">
            <CardHeader>
              <CardTitle className="text-orange-800 flex items-center">
                <Crown className="ml-2 w-5 h-5" />
                اختيار المحارب الناري
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {assessments.map((assessment) => (
                  <Button
                    key={assessment.id}
                    variant={selectedPlayer?.id === assessment.id ? "default" : "outline"}
                    onClick={() => setSelectedPlayer(assessment)}
                    className={`p-4 h-auto flex flex-col items-end text-right fire-glow ${
                      selectedPlayer?.id === assessment.id 
                        ? 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700' 
                        : 'border-orange-300 hover:bg-orange-50'
                    }`}
                  >
                    <span className="font-bold text-lg flex items-center">
                      <Fire className="w-4 h-4 ml-2" />
                      {assessment.player_name}
                    </span>
                    <span className="text-sm opacity-75 flex items-center">
                      <span>{assessment.position} • عمر {assessment.age}</span>
                      {assessment.total_coins > 0 && (
                        <Badge className="bg-yellow-100 text-yellow-800 mr-2">
                          <Coins className="w-3 h-3 ml-1" />
                          {assessment.total_coins}
                        </Badge>
                      )}
                    </span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-8 bg-gradient-to-r from-orange-200 to-red-200">
            <TabsTrigger value="assessment" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white fire-glow">
              🔥 التقييم
            </TabsTrigger>
            <TabsTrigger value="training" disabled={!selectedPlayer} className="data-[state=active]:bg-orange-600 data-[state=active]:text-white fire-glow">
              🚀 برامج التدريب
            </TabsTrigger>
            <TabsTrigger value="progress" disabled={!selectedPlayer} className="data-[state=active]:bg-orange-600 data-[state=active]:text-white fire-glow">
              🏆 تتبع التقدم
            </TabsTrigger>
            <TabsTrigger value="voice" disabled={!selectedPlayer} className="data-[state=active]:bg-orange-600 data-[state=active]:text-white fire-glow">
              🎤 المذكرات والإشعارات
            </TabsTrigger>
            <TabsTrigger value="group" disabled={!selectedPlayer} className="data-[state=active]:bg-orange-600 data-[state=active]:text-white fire-glow">
              👥 التدريب الجماعي
            </TabsTrigger>
          </TabsList>

          <TabsContent value="assessment">
            <AssessmentForm onAssessmentCreated={handleAssessmentCreated} />
          </TabsContent>

          <TabsContent value="training">
            {selectedPlayer && (
              <TrainingProgram 
                playerId={selectedPlayer.id} 
                playerName={selectedPlayer.player_name} 
              />
            )}
          </TabsContent>

          <TabsContent value="progress">
            {selectedPlayer && (
              <ProgressTracker 
                playerId={selectedPlayer.id} 
                playerName={selectedPlayer.player_name} 
              />
            )}
          </TabsContent>

          <TabsContent value="voice">
            {selectedPlayer && (
              <VoiceNotes 
                playerId={selectedPlayer.id} 
                playerName={selectedPlayer.player_name} 
              />
            )}
          </TabsContent>

          <TabsContent value="group">
            {selectedPlayer && (
              <GroupTraining 
                playerId={selectedPlayer.id} 
                playerName={selectedPlayer.player_name} 
              />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;