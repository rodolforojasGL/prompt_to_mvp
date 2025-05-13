'use client';
import React, { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || "http://localhost:8000/chat";

const App = () => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [previews, setPreviews] = useState<string[]>([]);
  const [selectedPreview, setSelectedPreview] = useState<number | null>(null);
  const [buildStatus, setBuildStatus] = useState<string | null>(null);
  const [theme, setTheme] = useState<"modern" | "retro" | "dark">("modern");

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: updatedMessages }),
      });
      const data = await response.json();
      const botMessage = { role: "assistant", content: data.content };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePreview = async () => {
    setLoading(true);
    setPreviews([]);
    setSelectedPreview(null);

    setTimeout(() => {
      setPreviews([
        "<div style='padding:1rem;'>Layout A<br/><button>Click me</button></div>",
        "<div style='padding:1rem;'>Layout B<br/><input placeholder='Type here' /></div>",
        "<div style='padding:1rem;'>Layout C<br/><ul><li>Item 1</li><li>Item 2</li></ul></div>",
      ]);
      setLoading(false);
    }, 1000);
  };

  const handleSelect = (index: number) => {
    setSelectedPreview(index);
  };

  const handleBuild = async () => {
    if (selectedPreview === null) return;
    setLoading(true);
    setBuildStatus(null);

    setTimeout(() => {
      setBuildStatus("Your app is ready! View or download coming soon.");
      setLoading(false);
    }, 1200);
  };

  const isRetro = theme === "retro";
  const isDark = theme === "dark";

  return (
    <body className="pixel-font">
    <div className={`p-6 max-w-3xl mx-auto min-h-screen transition-colors duration-500 ${isRetro ? "font-mono bg-black text-green-400" : isDark ? "bg-gray-900 text-white" : "bg-white text-gray-900"}`}>
      <div className="flex justify-between items-center mb-4">
        <h1 className={`text-3xl font-bold ${isRetro ? "text-pink-400 pixel-font" : "text-blue-600"}`}>🧠 AI App Generator</h1>
        <Select value={theme} onValueChange={(value) => setTheme(value as typeof theme)}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Select theme" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="modern">Modern</SelectItem>
            <SelectItem value="retro">Retro</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <ScrollArea className={`h-64 border rounded p-3 mb-4 overflow-y-auto ${isRetro ? "border-green-500 bg-black" : isDark ? "border-gray-700 bg-gray-800" : "bg-gray-50 border-gray-300"}`}>
        <div className="space-y-3">
          {messages.map((msg, idx) => (
            <div key={idx} className={`text-sm ${msg.role === "user" ? "text-right" : "text-left"}`}>
              <span className={`inline-block px-3 py-2 rounded-lg border ${msg.role === "user"
                  ? isRetro
                    ? "bg-green-800 text-white border-green-400"
                    : isDark
                      ? "bg-gray-700 text-white border-gray-500"
                      : "bg-blue-100 text-blue-800 border-blue-200"
                  : isRetro
                    ? "bg-green-900 text-green-300 border-green-600"
                    : isDark
                      ? "bg-gray-600 text-white border-gray-400"
                      : "bg-gray-200 text-gray-800 border-gray-300"}`}>
                {msg.content}
              </span>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      <div className="flex gap-2 mb-6">
        <Input
          className={`${isRetro ? "bg-green-950 text-green-300 border-green-600" : isDark ? "bg-gray-800 text-white border-gray-600" : ""}`}
          placeholder="Tell me what app you want to build..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <Button onClick={handleSendMessage} disabled={loading} className={`${isRetro ? "bg-pink-500 hover:bg-pink-400" : isDark ? "bg-gray-600 hover:bg-gray-500" : ""}`}>
          {loading ? <Loader className="animate-spin" /> : "Send"}
        </Button>
      </div>

      <Button onClick={handleGeneratePreview} disabled={loading || messages.length === 0} className={`${isRetro ? "bg-yellow-400 hover:bg-yellow-300 text-black" : isDark ? "bg-blue-600 hover:bg-blue-500" : ""}`}>
        {loading ? <Loader className="animate-spin" /> : "Generate Preview"}
      </Button>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {previews.map((html, i) => (
          <Card
            key={i}
            className={`cursor-pointer ${isRetro ? "border-green-400" : ""} ${selectedPreview === i ? "ring-2 ring-pink-500" : ""}`}
            onClick={() => handleSelect(i)}
          >
            <CardContent className={`p-4 ${isRetro ? "bg-green-900" : isDark ? "bg-gray-800" : "bg-white"}`}>
              <iframe
                srcDoc={html}
                title={`Preview ${i + 1}`}
                className={`w-full h-64 border ${isRetro ? "border-green-600" : isDark ? "border-gray-600" : "border-gray-300"}`}
              />
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedPreview !== null && (
        <div className="mt-6 space-y-4">
          <Button onClick={handleBuild} disabled={loading} className={`${isRetro ? "bg-blue-500 hover:bg-blue-400" : isDark ? "bg-indigo-600 hover:bg-indigo-500" : ""}`}>
            {loading ? <Loader className="animate-spin" /> : "Build App"}
          </Button>
          {buildStatus && <p className={`${isRetro ? "text-green-300" : isDark ? "text-green-400" : "text-green-700"} font-medium`}>{buildStatus}</p>}
        </div>
      )}
    </div>
    </body>
  );
};

export default App;
