'use client';

import React, { useState } from 'react';
import katex from 'katex';

interface MathTextProps {
  content: string;
  className?: string;
  block?: boolean;
}

function renderInlineFormatted(text: string): React.ReactNode[] {
  // Tách biểu thức toán học $$...$$ hoặc $...$ và inline code `...`
  const tokenRegex = /(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$|`[^`\n]+`|\*\*[^*\n]+\*\*)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, idx) => {
    if (!part) return null;

    if (part.startsWith('$$') && part.endsWith('$$') && part.length > 4) {
      const formula = part.slice(2, -2).trim();
      try {
        const html = katex.renderToString(formula, {
          displayMode: true,
          throwOnError: false,
        });
        return (
          <span
            key={idx}
            className="block my-2 overflow-x-auto"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        );
      } catch {
        return <code key={idx}>{formula}</code>;
      }
    }

    if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
      const formula = part.slice(1, -1).trim();
      try {
        const html = katex.renderToString(formula, {
          displayMode: false,
          throwOnError: false,
        });
        return (
          <span
            key={idx}
            className="inline-block align-middle mx-0.5"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        );
      } catch {
        return <code key={idx}>{formula}</code>;
      }
    }

    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return (
        <code
          key={idx}
          className="px-1.5 py-0.5 mx-0.5 rounded bg-indigo-500/15 border border-indigo-500/30 font-mono text-[0.9em] text-cyan-300"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return (
        <strong key={idx} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }

    return <React.Fragment key={idx}>{part}</React.Fragment>;
  });
}

function CodeBlockSnippet({ lang, code }: { lang: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      void navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    }
  };

  return (
    <div className="my-2.5 rounded-xl overflow-hidden border border-[#252538] bg-[#090910] text-left">
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#141422] border-b border-[#252538] text-xs text-slate-400 font-mono">
        <span>{lang || 'python'}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="px-2 py-0.5 rounded bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 transition cursor-pointer"
        >
          {copied ? '✓ Đã chép' : 'Sao chép'}
        </button>
      </div>
      <pre className="p-3 overflow-x-auto text-xs sm:text-sm font-mono text-emerald-300 leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function MathText({ content, className = '', block = false }: MathTextProps) {
  if (!content) return null;

  // Kiểm tra xem có fenced code block ```lang ... ``` không
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  const hasCodeBlock = content.includes('```');

  if (!hasCodeBlock && !content.includes('\n')) {
    const Wrapper = block ? 'div' : 'span';
    return <Wrapper className={className}>{renderInlineFormatted(content)}</Wrapper>;
  }

  const segments: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      const textChunk = content.slice(lastIndex, match.index);
      segments.push(
        <span key={`txt-${lastIndex}`} className="whitespace-pre-wrap">
          {renderInlineFormatted(textChunk)}
        </span>
      );
    }
    segments.push(
      <CodeBlockSnippet
        key={`code-${match.index}`}
        lang={match[1] || 'python'}
        code={match[2].trimEnd()}
      />
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    const remaining = content.slice(lastIndex);
    segments.push(
      <span key={`txt-${lastIndex}`} className="whitespace-pre-wrap">
        {renderInlineFormatted(remaining)}
      </span>
    );
  }

  const Wrapper = block ? 'div' : 'span';
  return <Wrapper className={className}>{segments}</Wrapper>;
}
