"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
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

interface Message {
  id: number;
  role: "user" | "assistant";
  question?: string;
  answer?: string;
  sources?: Source[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const askQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      question: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
          }),
        }
      );

      if (!res.ok) {
        const errorData = await res
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Something went wrong while processing your question."
        );
      }

      const data: ApiResponse = await res.json();

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        answer: data.answer,
        sources: data.sources,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to connect to Samvidhaan AI."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askQuestion();
    }
  };
  const copyAnswer = async (
    answer: string,
    messageId: number
  ) => {
    try {
      await navigator.clipboard.writeText(answer);

      setCopiedMessageId(messageId);

      setTimeout(() => {
        setCopiedMessageId(null);
      }, 2000);
    } catch {
      setError("Unable to copy the answer.");
    }
  };
  const startNewConversation = () => {
    setMessages([]);
    setQuestion("");
    setError("");
  };

  return (
    <main className="min-h-screen bg-[#f7f4ed] text-[#172018]">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="sticky top-0 z-10 border-b border-[#ded8ca] bg-[#f7f4ed]/95 backdrop-blur">

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

          {messages.length > 0 && (
            <button
              onClick={startNewConversation}
              className="rounded-xl border border-[#cfc7b7] bg-white px-4 py-2 text-xs font-semibold text-[#465047] transition hover:border-[#315d45] hover:text-[#315d45]"
            >
              + New Conversation
            </button>
          )}

        </div>

      </header>


      {/* ================================================== */}
      {/* MAIN */}
      {/* ================================================== */}

      <section className="mx-auto flex min-h-[calc(100vh-82px)] max-w-5xl flex-col px-6 py-10">

        {/* ================================================== */}
        {/* HERO */}
        {/* ================================================== */}

        {messages.length === 0 && !loading && (

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

              Ask questions about the Constitution of India
              and receive answers grounded in the
              constitutional text.

            </p>

            <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">

              {[
                "What are Fundamental Rights?",
                "What does Article 368 say?",
                "What is the Right to Education?",
              ].map((example) => (

                <button
                  key={example}
                  onClick={() =>
                    setQuestion(example)
                  }
                  className="rounded-full border border-[#d4cec0] bg-white px-4 py-2 text-[#465047] transition hover:border-[#315d45] hover:text-[#315d45]"
                >
                  {example}
                </button>

              ))}

            </div>

          </div>

        )}


        {/* ================================================== */}
        {/* CHAT */}
        {/* ================================================== */}

        {messages.length > 0 && (

          <div className="flex-1 space-y-8 pb-8">

            {messages.map((message) => (

              <div key={message.id}>

                {/* USER MESSAGE */}

                {message.role === "user" && (

                  <div className="flex justify-end">

                    <div className="max-w-2xl rounded-2xl rounded-br-md bg-[#173b2a] px-5 py-4 text-[15px] leading-7 text-white shadow-sm">

                      {message.question}

                    </div>

                  </div>

                )}


                {/* ASSISTANT MESSAGE */}

                {message.role === "assistant" && (

                  <div className="max-w-4xl">

                    <div className="mb-4 flex items-center gap-3">

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


                    {/* ANSWER */}

                    <div className="rounded-2xl rounded-tl-md border border-[#ddd7ca] bg-white p-6 shadow-sm sm:p-8">
                      <div className="mb-5 flex justify-end">
                        <button
                          onClick={() =>
                            copyAnswer(
                              message.answer || "",
                              message.id
                            )
                          }
                          className="rounded-lg border border-[#d7d1c4] px-3 py-1.5 text-xs font-medium text-[#596158] transition hover:border-[#315d45] hover:text-[#315d45]"
                        >
                          {copiedMessageId === message.id
                            ? "✓ Copied"
                            : "Copy Answer"}
                        </button>
                      </div>
                      <div className="text-[15px] leading-7 text-[#303830]">
                        
                        <ReactMarkdown
                          components={{
                            h1: ({ children }) => (
                              <h1 className="mb-4 text-2xl font-bold">
                                {children}
                              </h1>
                            ),

                            h2: ({ children }) => (
                              <h2 className="mb-3 mt-6 text-xl font-bold">
                                {children}
                              </h2>
                            ),
                          
                            h3: ({ children }) => (
                              <h3 className="mb-2 mt-5 text-lg font-semibold">
                                {children}
                              </h3>
                            ),

                            p: ({ children }) => (
                              <p className="mb-4 last:mb-0">
                                {children}
                              </p>
                            ),

                            strong: ({ children }) => (
                              <strong className="font-semibold text-[#172018]">
                                {children}
                              </strong>
                            ),

                            ul: ({ children }) => (
                              <ul className="mb-4 ml-6 list-disc space-y-2">
                                {children}
                              </ul>
                            ),

                            ol: ({ children }) => (
                              <ol className="mb-4 ml-6 list-decimal space-y-2">
                                {children}
                              </ol>
                            ),

                            li: ({ children }) => (
                              <li className="pl-1">
                                {children}
                              </li>
                            ),

                            blockquote: ({ children }) => (
                              <blockquote className="my-4 border-l-4 border-[#315d45] pl-4 italic text-[#596158]">
                                {children}
                              </blockquote>
                            ),

                            code: ({ children }) => (
                              <code className="rounded bg-[#f1eee7] px-1.5 py-0.5 font-mono text-sm">
                                {children}
                              </code>
                            ),
                          }}
                        >
                          {message.answer}
                        </ReactMarkdown>
                      </div>

                    </div>


                    {/* SOURCES */}

                    {message.sources &&
                      message.sources.length > 0 && (

                        <div className="mt-5">

                          <div className="mb-3">

                            <h3 className="text-sm font-semibold">
                              Constitutional Sources
                            </h3>

                            <p className="text-xs text-[#747b73]">
                              Retrieved from the
                              constitutional database.
                            </p>

                          </div>


                          <div className="grid gap-3 sm:grid-cols-2">

                            {message.sources.map(
                              (source, index) => (

                                <div
                                  key={`${source.article}-${index}`}
                                  className="rounded-xl border border-[#ddd7ca] bg-white p-4 shadow-sm"
                                >

                                  <span className="inline-block rounded-full bg-[#e7eee8] px-3 py-1 text-xs font-semibold text-[#315d45]">
                                    Article{" "}
                                    {source.article}
                                  </span>

                                  <h4 className="mt-3 font-semibold leading-6">
                                    {source.title}
                                  </h4>

                                  <p className="mt-1 text-sm text-[#737a72]">
                                    {source.part}
                                  </p>

                                  {source.part_title && (
                                    <p className="mt-1 text-xs text-[#92978f]">
                                      {source.part_title}
                                    </p>
                                  )}

                                </div>

                              )
                            )}

                          </div>

                        </div>

                      )}

                  </div>

                )}

              </div>

            ))}


            {/* ================================================== */}
            {/* LOADING */}
            {/* ================================================== */}

            {loading && (

              <div className="max-w-4xl">

                <div className="mb-4 flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#173b2a] text-[#f4d06f]">
                    ⚖
                  </div>

                  <div>
                    <p className="font-semibold">
                      Samvidhaan AI
                    </p>

                    <p className="text-xs text-[#7b827b]">
                      Working on your question
                    </p>
                  </div>

                </div>


                <div className="rounded-2xl rounded-tl-md border border-[#ddd7ca] bg-white p-6 shadow-sm">

                  <div className="flex items-center gap-3">

                    <div className="flex gap-1">

                      <span className="h-2 w-2 animate-bounce rounded-full bg-[#315d45]" />

                      <span className="h-2 w-2 animate-bounce rounded-full bg-[#315d45] [animation-delay:150ms]" />

                      <span className="h-2 w-2 animate-bounce rounded-full bg-[#315d45] [animation-delay:300ms]" />

                    </div>

                    <span className="text-sm text-[#747b73]">
                      Retrieving constitutional context...
                    </span>

                  </div>

                </div>

              </div>

            )}

            <div ref={messagesEndRef} />

          </div>

        )}


        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && !loading && (

          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>

        )}


        {/* ================================================== */}
        {/* INPUT */}
        {/* ================================================== */}

        <div className="mt-auto">

          <div className="rounded-2xl border border-[#d7d1c4] bg-white p-3 shadow-sm">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
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
            Samvidhaan AI provides answers based on
            available constitutional context.
          </p>

        </div>

      </section>

    </main>
  );
}