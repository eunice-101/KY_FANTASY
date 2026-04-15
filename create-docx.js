const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "C8A96E", font: "맑은 고딕", size: 20 })] })]
  });
}

function cell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "맑은 고딕", size: 20 })] })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "맑은 고딕", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "맑은 고딕", color: "1A1A2E" },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "맑은 고딕", color: "8B1A1A" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "맑은 고딕", color: "2D6A4F" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1440, hanging: 360 } } } }
      ]},
      { reference: "workflow", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1\uB2E8\uACC4", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 720 } } } }
      ]},
      { reference: "numbers", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
      ]}
    ]
  },
  sections: [
    // ===== 표지 =====
    {
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 3600, right: 1440, bottom: 1440, left: 1440 } }
      },
      children: [
        new Paragraph({ spacing: { after: 600 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
          new TextRun({ text: "KY Fantasy", font: "맑은 고딕", size: 60, bold: true, color: "1A1A2E" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
          new TextRun({ text: "\u2694 \uD310\uD0C0\uC9C0 \uC18C\uC124 \uC790\uB3D9\uD654 \uC2DC\uC2A4\uD15C \u2694", font: "맑은 고딕", size: 32, color: "C8A96E" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [
          new TextRun({ text: "\uD1B5\uD569 \uC124\uACC4 \uC6CC\uD06C\uD50C\uB85C\uC6B0", font: "맑은 고딕", size: 28, color: "8B1A1A" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "C8A96E", space: 1 } },
          spacing: { after: 400 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
          new TextRun({ text: "Claude Opus 4.6 \uAE30\uBC18", font: "맑은 고딕", size: 22, color: "666666" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "2026\uB144 4\uC6D4", font: "맑은 고딕", size: 22, color: "666666" })
        ]}),
      ]
    },
    // ===== 본문 =====
    {
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      headers: {
        default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "KY Fantasy \u2014 \uD1B5\uD569 \uC124\uACC4 \uC6CC\uD06C\uD50C\uB85C\uC6B0", font: "맑은 고딕", size: 16, color: "999999" })] })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: "맑은 고딕", size: 16, color: "999999" })] })] })
      },
      children: [
        // 1. 개요
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. \uAC1C\uC694")] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("\uC2DC\uC2A4\uD15C \uBAA9\uC801")] }),
        new Paragraph({ spacing: { after: 120 }, children: [
          new TextRun("Claude Opus 4.6 AI\uB97C \uD65C\uC6A9\uD558\uC5EC \uD55C\uAD6D\uC5B4 \uD310\uD0C0\uC9C0 \uC18C\uC124\uC744 \uC790\uB3D9\uC73C\uB85C \uC0DD\uC131\uD558\uB294 \uD1B5\uD569 \uC2DC\uC2A4\uD15C\uC785\uB2C8\uB2E4. "),
          new TextRun({ text: "webnovel-writer", bold: true }),
          new TextRun("\uC758 \uD558\uC774\uBE0C\uB9AC\uB4DC RAG \uC5D4\uC9C4, "),
          new TextRun({ text: "Claude-Code-Novel-Writer", bold: true }),
          new TextRun("\uC758 8\uB2E8\uACC4 \uC624\uCF00\uC2A4\uD2B8\uB808\uC774\uC158, "),
          new TextRun({ text: "Claude-Book", bold: true }),
          new TextRun("\uC758 \uD488\uC9C8 \uAC8C\uC774\uD2B8\uB97C \uD1B5\uD569\uD569\uB2C8\uB2E4.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("\uC18C\uC124 \uC124\uC815")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "\uC7A5\uB974: ", bold: true }), new TextRun("\uD55C\uAD6D \uC6F9\uD230 \uC2A4\uD0C0\uC77C + \uD310\uD0C0\uC9C0 \uBB34\uD611 \uC735\uD569")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "\uBE44\uC8FC\uC5BC: ", bold: true }), new TextRun("\uC12C\uC138\uD558\uACE0 \uC720\uB824\uD55C \uC120\uD654, \uAC10\uC131\uC801 \uC870\uBA85, \uC218\uCC44\uD654 \uAC19\uC740 \uB514\uC9C0\uD138 \uCC44\uC0C9")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [
          new TextRun({ text: "\uC8FC\uC778\uACF5: ", bold: true }), new TextRun("\uC18C\uBC15\uD55C \uBCF5\uC7A5\uC758 \uC544\uB984\uB2E4\uC6B4 \uD751\uBC1C \uC18C\uB140, \uB180\uB78C\uACFC \uD638\uAE30\uC2EC\uC774 \uC11E\uC778 \uD45C\uC815")] }),

        // 2. 전체 워크플로우
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. \uC804\uCCB4 \uC6CC\uD06C\uD50C\uB85C\uC6B0 (10\uB2E8\uACC4)")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("1\uB2E8\uACC4: \uD504\uB85C\uC81D\uD2B8 \uCD08\uAE30\uD654")] }),
        new Paragraph({ spacing: { after: 60 }, children: [
          new TextRun({ text: "python ky_engine.py init \"\uC18C\uC124 \uC81C\uBAA9\"", font: "Consolas", size: 20, color: "2D6A4F" })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun(".webnovel/ \uB514\uB809\uD1A0\uB9AC \uC0DD\uC131, state.json \uCD08\uAE30\uD654")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("index.db, vectors.db SQLite \uB370\uC774\uD130\uBCA0\uC774\uC2A4 \uC0DD\uC131")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("2\uB2E8\uACC4: \uC138\uACC4\uAD00 \uC124\uACC4")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("worldbuilder \uC5D0\uC774\uC804\uD2B8 \uD638\uCD9C")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("\uB9C8\uBC95 \uCCB4\uACC4, \uC9C0\uB9AC, \uC5ED\uC0AC, \uBB38\uD654, \uC138\uB825 \uAD6C\uB3C4 \uC124\uACC4 \u2192 bible/world.md \uC800\uC7A5")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3\uB2E8\uACC4: \uCE90\uB9AD\uD130 \uBC14\uC774\uBE14 \uC791\uC131")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("character-developer \uC5D0\uC774\uC804\uD2B8 \uD638\uCD9C")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("\uC8FC\uC778\uACF5/\uC870\uB825\uC790/\uC545\uB2F9 \uC2EC\uB9AC+\uC131\uC7A5 \uC544\uD06C \uC124\uACC4 \u2192 bible/characters/*.md")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("4\uB2E8\uACC4: 30\uCC55\uD130 \uD50C\uB86F \uC124\uACC4")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("plot-architect \uC5D0\uC774\uC804\uD2B8 \uD638\uCD9C")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("5\uB9C9 \uAD6C\uC870: \uB3C4\uC785(1-5) \u2192 \uC804\uAC1C(6-15) \u2192 \uC704\uAE30(16-20) \u2192 \uBC18\uC804(21-25) \u2192 \uACB0\uB9D0(26-30)")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("5\uB2E8\uACC4: \uBD88\uBCC0 \uBC14\uC774\uBE14 \uD655\uC815")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("bible/ \uD3F4\uB354 \uC77D\uAE30 \uC804\uC6A9\uC73C\uB85C \uC7A0\uAE08 \u2014 \uC0DD\uC131 \uC911 \uC808\uB300 \uC218\uC815 \uAE08\uC9C0")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("6\uB2E8\uACC4: \uCC55\uD130 \uC0DD\uC131 \uB8E8\uD504")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("\uCEE8\uD14D\uC2A4\uD2B8 \uC870\uB9BD \u2192 Claude Opus \uD638\uCD9C \u2192 \uD488\uC9C8 \uAC8C\uC774\uD2B8 3\uC911 \uAC80\uC99D")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("\uCD5C\uB300 3\uD68C \uC7AC\uC2DC\uB3C4 \uD6C4 \uC2B9\uC778 \u2192 story/chapters/ \uC800\uC7A5")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("7\uB2E8\uACC4: \uC0C1\uD0DC \uC5C5\uB370\uC774\uD2B8")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("state/chapter-NN/ \uC2A4\uB0C5\uC0F7 \uC0DD\uC131")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("timeline/current-chapter.md \u2192 timeline/history.md \uCD94\uAC00(\uCD94\uAC00 \uC804\uC6A9)")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("8\uB2E8\uACC4: \uB9C8\uC77C\uC2A4\uD1A4 \uC810\uAC80")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("5\uCC55\uD130\uB9C8\uB2E4 smart-planner \uC5D0\uC774\uC804\uD2B8: \uD398\uC774\uC2F1 \uBD84\uC11D, \uBCF5\uC120 \uCD94\uC801, \uBC29\uD5A5 \uC870\uC815")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("9\uB2E8\uACC4: \uC644\uB8CC \uBC0F \uB2E4\uB4EC\uAE30")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [new TextRun("30\uCC55\uD130 \uC644\uB8CC \u2192 \uCD5C\uC885 \uAC80\uD1A0 \uBC0F \uD3F4\uB9AC\uC2F1")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("10\uB2E8\uACC4: \uB300\uC2DC\uBCF4\uB4DC \uBAA8\uB2C8\uD130\uB9C1")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 240 }, children: [new TextRun("http://127.0.0.1:8765 \uC5D0\uC11C \uC2E4\uC2DC\uAC04 \uC9C4\uD589 \uC0C1\uD669 \uD655\uC778")] }),

        // 3. 챕터 생성 상세 워크플로우
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. \uCC55\uD130 \uC0DD\uC131 \uC0C1\uC138 \uC6CC\uD06C\uD50C\uB85C\uC6B0")] }),

        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("\uAC01 \uCC55\uD130\uB294 \uB2E4\uC74C \uD30C\uC774\uD504\uB77C\uC778\uC744 \uAC70\uCE69\uB2C8\uB2E4:")] }),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [1800, 3200, 4026],
          rows: [
            new TableRow({ children: [headerCell("\uB2E8\uACC4", 1800), headerCell("\uC791\uC5C5", 3200), headerCell("\uC0C1\uC138", 4026)] }),
            new TableRow({ children: [cell("1. \uCEE8\uD14D\uC2A4\uD2B8", 1800), cell("ContextManager.build_context()", 3200), cell("\uAC00\uC911\uCE58 \uAE30\uBC18 \uCEE8\uD14D\uC2A4\uD2B8 \uC870\uB9BD (core/scene/global/genre/memory)", 4026)] }),
            new TableRow({ children: [cell("2. \uC0DD\uC131", 1800), cell("Claude Opus 4.6 \uD638\uCD9C", 3200), cell("thinking=adaptive, \uC2A4\uD2B8\uB9AC\uBC0D, 5000-8000\uC790", 4026)] }),
            new TableRow({ children: [cell("3. \uBB38\uCCB4 \uAC80\uC99D", 1800), cell("style-linter \uC5D0\uC774\uC804\uD2B8", 3200), cell("AI \uD328\uD134 \uAC10\uC9C0, \uBB38\uC7A5 \uAE38\uC774, \uB300\uD654 \uBE44\uC728", 4026)] }),
            new TableRow({ children: [cell("4. \uCE90\uB9AD\uD130 \uAC80\uC99D", 1800), cell("character-developer", 3200), cell("\uB9D0\uD22C \uC77C\uAD00\uC131, \uC815\uBCF4 \uBC94\uC704, \uC2EC\uB9AC \uBCC0\uD654", 4026)] }),
            new TableRow({ children: [cell("5. \uC5F0\uC18D\uC131 \uAC80\uC99D", 1800), cell("continuity-editor", 3200), cell("\uD0C0\uC784\uB77C\uC778, \uACF5\uAC04 \uB17C\uB9AC, \uC138\uACC4\uAD00 \uADDC\uCE59", 4026)] }),
            new TableRow({ children: [cell("6. \uD310\uC815", 1800), cell("\uD1B5\uACFC/\uC7AC\uC2DC\uB3C4", 3200), cell("\uCD5C\uB300 3\uD68C \uBC18\uBCF5 \uD6C4 \uC2B9\uC778", 4026)] }),
            new TableRow({ children: [cell("7. \uC800\uC7A5", 1800), cell("RAG + State + Timeline", 3200), cell("\uBCA1\uD130DB \uC800\uC7A5, \uC0C1\uD0DC \uC5C5\uB370\uC774\uD2B8, \uD0C0\uC784\uB77C\uC778 \uCD94\uAC00", 4026)] }),
          ]
        }),

        // 4. 에이전트 역할
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. 8\uAC1C \uC5D0\uC774\uC804\uD2B8 \uC5ED\uD560")] }),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2200, 2400, 4426],
          rows: [
            new TableRow({ children: [headerCell("\uC5D0\uC774\uC804\uD2B8", 2200), headerCell("\uC5ED\uD560", 2400), headerCell("\uC0C1\uC138 \uC124\uBA85", 4426)] }),
            new TableRow({ children: [cell("chapter-writer", 2200), cell("\uCC55\uD130 \uC9D1\uD544", 2400), cell("5000-8000\uC790 \uD55C\uAD6D\uC5B4 \uD310\uD0C0\uC9C0 \uCC55\uD130 \uC0DD\uC131. \uBE44\uD2B8 \uC2DC\uD2B8 \uAE30\uBC18, \uC2A4\uD2B8\uB9AC\uBC0D \uCD9C\uB825", 4426)] }),
            new TableRow({ children: [cell("plot-architect", 2200), cell("\uD50C\uB86F \uC124\uACC4", 2400), cell("30\uCC55\uD130 \uC544\uC6C3\uB77C\uC778, \uCC55\uD130\uBCC4 \uBE44\uD2B8 \uC2DC\uD2B8, \uD398\uC774\uC2F1 \uCD5C\uC801\uD654", 4426)] }),
            new TableRow({ children: [cell("worldbuilder", 2200), cell("\uC138\uACC4\uAD00 \uC124\uACC4", 2400), cell("\uB9C8\uBC95 \uCCB4\uACC4, \uC9C0\uB9AC, \uC5ED\uC0AC, \uBB38\uD654, \uC138\uB825 \uAD6C\uB3C4 \uC124\uACC4", 4426)] }),
            new TableRow({ children: [cell("character-developer", 2200), cell("\uCE90\uB9AD\uD130 \uAC1C\uBC1C/\uAC80\uC99D", 2400), cell("\uCE90\uB9AD\uD130 \uBC14\uC774\uBE14 \uC791\uC131 + \uCC55\uD130 \uB0B4 \uC77C\uAD00\uC131 \uAC80\uC99D", 4426)] }),
            new TableRow({ children: [cell("continuity-editor", 2200), cell("\uC5F0\uC18D\uC131 \uAC80\uC99D", 2400), cell("\uD0C0\uC784\uB77C\uC778/\uACF5\uAC04 \uB17C\uB9AC/\uC815\uBCF4 \uC77C\uAD00\uC131/\uC138\uACC4\uAD00 \uADDC\uCE59 \uAC80\uC99D", 4426)] }),
            new TableRow({ children: [cell("smart-planner", 2200), cell("\uC804\uB7B5 \uBD84\uC11D", 2400), cell("5\uCC55\uD130\uB9C8\uB2E4 \uD398\uC774\uC2F1/\uBCF5\uC120/\uD488\uC9C8 \uBD84\uC11D \uBC0F \uBC29\uD5A5 \uC870\uC815", 4426)] }),
            new TableRow({ children: [cell("style-linter", 2200), cell("\uBB38\uCCB4 \uAC80\uC99D", 2400), cell("AI \uD328\uD134 \uAC10\uC9C0, \uBB38\uC7A5 \uB9AC\uB4EC, \uB300\uD654 \uBE44\uC728, \uD074\uB9AC\uC170 \uCC28\uB2E8", 4426)] }),
            new TableRow({ children: [cell("error-recovery", 2200), cell("\uC624\uB958 \uBCF5\uAD6C", 2400), cell("\uD30C\uC77C \uC190\uC0C1/\uC0C1\uD0DC \uBD88\uC77C\uCE58/JSON \uC624\uB958 \uC9C4\uB2E8 \uBC0F \uC790\uB3D9 \uBCF5\uAD6C", 4426)] }),
          ]
        }),

        // 5. 파일 구조
        new Paragraph({ spacing: { before: 400 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("5. \uD30C\uC77C \uAD6C\uC870")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun({ text: "KY_Fantasy/\n\u251C\u2500\u2500 CLAUDE.md              \u2190 \uB9C8\uC2A4\uD130 \uC624\uCF00\uC2A4\uD2B8\uB808\uC774\uD130\n\u251C\u2500\u2500 ky_engine.py           \u2190 \uD575\uC2EC \uC5D4\uC9C4 (Python CLI)\n\u251C\u2500\u2500 ky_prompts.py          \u2190 \uD55C\uAD6D\uC5B4 \uD310\uD0C0\uC9C0 \uD504\uB86C\uD504\uD2B8\n\u251C\u2500\u2500 bible/                 \u2190 \uBD88\uBCC0 \uC2A4\uD1A0\uB9AC \uBC14\uC774\uBE14\n\u251C\u2500\u2500 state/                 \u2190 \uBC84\uC804\uAD00\uB9AC \uC0C1\uD0DC\n\u251C\u2500\u2500 timeline/              \u2190 \uCD94\uAC00 \uC804\uC6A9 \uD0C0\uC784\uB77C\uC778\n\u251C\u2500\u2500 story/chapters/        \u2190 \uCD5C\uC885 \uCC55\uD130 \uD30C\uC77C\n\u251C\u2500\u2500 planning/              \u2190 JSON \uC0C1\uD0DC \uCD94\uC801\n\u251C\u2500\u2500 .claude/agents/        \u2190 8\uAC1C \uC804\uBB38 \uC5D0\uC774\uC804\uD2B8\n\u251C\u2500\u2500 web/                   \u2190 Flask \uB300\uC2DC\uBCF4\uB4DC\n\u2514\u2500\u2500 webnovel-writer/       \u2190 RAG + SQLite \uCF54\uC5B4 \uC5D4\uC9C4",
            font: "Consolas", size: 18 })
        ]}),

        // 6. 품질 관리
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. \uD488\uC9C8 \uAD00\uB9AC \uCCB4\uACC4")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("\uC801\uC751\uD615 \uD488\uC9C8 \uBAA8\uB4DC")] }),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [1500, 2500, 5026],
          rows: [
            new TableRow({ children: [headerCell("\uD488\uC9C8 \uC810\uC218", 1500), headerCell("\uBAA8\uB4DC", 2500), headerCell("\uC804\uB7B5", 5026)] }),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, shading: { fill: "D4EDDA", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "\u2265 90\uC810", bold: true })] })] }),
              cell("\uCD5C\uACE0 \uD488\uC9C8 \uBAA8\uB4DC", 2500), cell("\uCD9C\uD310 \uC900\uBE44 \uC218\uC900. \uC138\uC2EC\uD55C \uB2E4\uB4EC\uAE30 \uC9C4\uD589", 5026)] }),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, shading: { fill: "CCE5FF", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "80-89\uC810", bold: true })] })] }),
              cell("\uACE0\uC131\uB2A5 \uBAA8\uB4DC", 2500), cell("\uBAA8\uBA58\uD140 \uC720\uC9C0. \uC0AC\uC18C\uD55C \uD488\uC9C8 \uC774\uC288 \uD5C8\uC6A9", 5026)] }),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, shading: { fill: "FFF3CD", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "60-79\uC810", bold: true })] })] }),
              cell("\uD45C\uC900 \uBAA8\uB4DC", 2500), cell("\uD488\uC9C8\uACFC \uC18D\uB3C4 \uADE0\uD615", 5026)] }),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 1500, type: WidthType.DXA }, shading: { fill: "F8D7DA", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "< 60\uC810", bold: true })] })] }),
              cell("\uD488\uC9C8 \uC9D1\uC911 \uBAA8\uB4DC", 2500), cell("\uAE30\uC900 \uC0C1\uD5A5. \uCD5C\uADFC \uCF58\uD150\uCE20 \uC7AC\uAC80\uD1A0", 5026)] }),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("AI \uD328\uD134 \uAC10\uC9C0 \uAE30\uC900")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("\uACFC\uB3C4\uD55C \uB098\uC5F4\uD615 \uBB38\uC7A5 (\"\uCCAB\uC9F8...\uB458\uC9F8...\uC14B\uC9F8...\")")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("\uD310\uC5D0 \uBC15\uD78C \uAC10\uC815 \uD45C\uD604 \uBC18\uBCF5")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("\uD55C \uBB38\uB2E8\uC5D0 \uB3D9\uC77C \uB2E8\uC5B4 3\uD68C \uC774\uC0C1 \uBC18\uBCF5")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("\uAE30\uACC4\uC801\uC73C\uB85C \uC644\uBCBD\uD55C \uB300\uD654 \uAD6C\uC870")] }),

        // 7. 기술 스택
        new Paragraph({ spacing: { before: 400 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("7. \uAE30\uC220 \uC2A4\uD0DD")] }),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2500, 2500, 4026],
          rows: [
            new TableRow({ children: [headerCell("\uCEF4\uD3EC\uB10C\uD2B8", 2500), headerCell("\uAE30\uC220", 2500), headerCell("\uC5ED\uD560", 4026)] }),
            new TableRow({ children: [cell("AI \uBAA8\uB378", 2500), cell("Claude Opus 4.6", 2500), cell("\uCC55\uD130 \uC0DD\uC131, \uC138\uACC4\uAD00 \uC124\uACC4, \uD488\uC9C8 \uAC80\uC99D", 4026)] }),
            new TableRow({ children: [cell("RAG \uC5D4\uC9C4", 2500), cell("webnovel-writer", 2500), cell("\uD558\uC774\uBE0C\uB9AC\uB4DC \uAC80\uC0C9 (\uBCA1\uD130+BM25+\uADF8\uB798\uD504)", 4026)] }),
            new TableRow({ children: [cell("\uB370\uC774\uD130\uBCA0\uC774\uC2A4", 2500), cell("SQLite", 2500), cell("index.db (\uC5D4\uD2F0\uD2F0/\uBD80\uCC44/\uC7A5\uBA74) + vectors.db", 4026)] }),
            new TableRow({ children: [cell("\uC6F9 \uB300\uC2DC\uBCF4\uB4DC", 2500), cell("Flask 3.0", 2500), cell("\uC9C4\uD589 \uD604\uD669 \uBAA8\uB2C8\uD130\uB9C1, API \uC5D4\uB4DC\uD3EC\uC778\uD2B8", 4026)] }),
            new TableRow({ children: [cell("\uC624\uCF00\uC2A4\uD2B8\uB808\uC774\uC158", 2500), cell("Claude Code + CLAUDE.md", 2500), cell("8\uB2E8\uACC4 \uACB0\uC815 \uB9E4\uD2B8\uB9AD\uC2A4 \uAE30\uBC18 \uC790\uB3D9\uD654", 4026)] }),
            new TableRow({ children: [cell("\uC5B8\uC5B4", 2500), cell("Python 3.10+", 2500), cell("ky_engine.py \uB2E8\uC77C \uC9C4\uC785\uC810, Windows \uD638\uD658", 4026)] }),
          ]
        }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\10_17\\Desktop\\KY_Fantasy\\integrated-design.docx", buffer);
  console.log("integrated-design.docx created successfully");
});
