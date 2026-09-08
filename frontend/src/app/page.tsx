"use client";

import { useState } from "react";

interface Source {
  article: string;
  title: string;
  part: string;
  part_title?: string;
}

interface ApiResponse {
  question: string;
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Something went wrong."
        );
      }

      const data: ApiResponse = await res.json();

      setResponse(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to connect to Samvidhaan AI.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  return (
    <main className="min-h-screen bg-[#f7f4ed] text-[#172018]">
      
      {/* Header */}
      <header className="border-b border-[#ded8ca] bg-[#f7f4ed]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#173b2a] text-xl text-[#f4d06f]">
              ⚖
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Samvidhaan AI
              </h1>

              <p className="text-xs text-[#667066]">
                Indian Constitution Research Assistant
              </p>
            </div>
          </div>

          <div className="hidden rounded-full border border-[#cfc7b7] px-4 py-2 text-xs font-medium text-[#596158] sm:block">
            Constitutional Research
          </div>
        </div>
      </header>


      {/* Main */}
      <section className="mx-auto flex min-h-[calc(100vh-82px)] max-w-5xl flex-col px-6 py-12">
        
        {/* Hero */}
        {!response && !loading && (
          <div className="flex flex-1 flex-col items-center justify-center text-center">
            
            <div className="mb-6 rounded-full border border-[#d8cda9] bg-[#eee8d5] px-4 py-2 text-sm font-medium text-[#6c5b27]">
              🇮🇳 Constitution of India
            </div>

            <h2 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
              Understand the Constitution.
              <span className="block text-[#315d45]">
                Ask Samvidhaan AI.
              </span>
            </h2>

            <p className="mt-5 max-w-2xl text-base leading-7 text-[#697168]">
              Ask questions about the Constitution of India and receive
              answers grounded in the constitutional text.
            </p>

            <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
              {[
                "What are Fundamental Rights?",
                "What does Article 368 say?",
                "What is the Right to Education?",
              ].map((example) => (
                <button
                  key={example}
                  onClick={() => setQuestion(example)}
                  className="rounded-full border border-[#d4cec0] bg-white px-4 py-2 text-[#465047] transition hover:border-[#315d45] hover:text-[#315d45]"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}


        {/* Answer */}
        {response && (
          <div className="flex-1">
            
            <div className="mb-8">
              <p className="mb-2 text-sm font-medium text-[#7a8179]">
                YOUR QUESTION
              </p>

              <h2 className="text-2xl font-semibold leading-9">
                {response.question}
              </h2>
            </div>


            {/* Answer Card */}
            <div className="rounded-2xl border border-[#ddd7ca] bg-white p-6 shadow-sm sm:p-8">
              
              <div className="mb-5 flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#173b2a] text-[#f4d06f]">
                  ⚖
                </div>

                <div>
                  <p className="font-semibold">
                    Samvidhaan AI
                  </p>

                  <p className="text-xs text-[#7b827b]">
                    Constitutional answer
                  </p>
                </div>
              </div>

              <div className="whitespace-pre-wrap text-[15px] leading-7 text-[#303830]">
                {response.answer}
              </div>
            </div>


            {/* Sources */}
            {response.sources.length > 0 && (
              <div className="mt-8">
                
                <div className="mb-4">
                  <h3 className="text-lg font-semibold">
                    Constitutional Sources
                  </h3>

                  <p className="text-sm text-[#747b73]">
                    Articles retrieved from the constitutional database.
                  </p>
                </div>


                <div className="grid gap-4 sm:grid-cols-2">
                  {response.sources.map((source, index) => (
                    <div
                      key={`${source.article}-${index}`}
                      className="rounded-xl border border-[#ddd7ca] bg-white p-5 shadow-sm"
                    >
                      <div className="mb-3 flex items-center justify-between">
                        
                        <span className="rounded-full bg-[#e7eee8] px-3 py-1 text-xs font-semibold text-[#315d45]">
                          Article {source.article}
                        </span>

                      </div>

                      <h4 className="font-semibold leading-6">
                        {source.title}
                      </h4>

                      <p className="mt-2 text-sm text-[#737a72]">
                        {source.part}
                      </p>

                      {source.part_title && (
                        <p className="mt-1 text-xs text-[#92978f]">
                          {source.part_title}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}


            {/* Ask another */}
            <button
              onClick={() => {
                setResponse(null);
                setQuestion("");
              }}
              className="mt-8 rounded-xl border border-[#cfc8ba] px-5 py-3 text-sm font-medium text-[#465047] transition hover:bg-white"
            >
              ← Ask another question
            </button>
          </div>
        )}


        {/* Loading */}
        {loading && (
          <div className="flex flex-1 items-center justify-center">
            <div className="text-center">
              
              <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full border-4 border-[#d8dfd9] border-t-[#315d45] animate-spin" />

              <h3 className="font-semibold">
                Searching the Constitution...
              </h3>

              <p className="mt-2 text-sm text-[#777e76]">
                Retrieving constitutional context and generating an answer.
              </p>
            </div>
          </div>
        )}


        {/* Error */}
        {error && !loading && (
          <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}


        {/* Input */}
        {!response && !loading && (
          <div className="mt-auto">
            
            <div className="rounded-2xl border border-[#d7d1c4] bg-white p-3 shadow-sm">
              
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about the Constitution..."
                rows={3}
                className="w-full resize-none bg-transparent px-3 py-2 text-[15px] outline-none placeholder:text-[#9a9f99]"
              />

              <div className="flex items-center justify-between border-t border-[#eeeae1] pt-3">
                
                <p className="hidden text-xs text-[#92978f] sm:block">
                  Press Enter to ask • Shift + Enter for a new line
                </p>

                <button
                  onClick={askQuestion}
                  disabled={loading}
                  className="ml-auto rounded-xl bg-[#173b2a] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#245239] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Ask Samvidhaan →
                </button>

              </div>
            </div>

            <p className="mt-3 text-center text-xs text-[#969b94]">
              Samvidhaan AI provides answers based on available
              constitutional context.
            </p>
          </div>
        )}

      </section>
    </main>
  );
}