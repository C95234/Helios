import { useMemo } from "react";
import katex from "katex";

/** Rendu LaTeX reel (KaTeX) -- §3 : le mode expert doit afficher les formules
 * en rendu mathematique, pas en texte brut. `block` = affichage centre (display mode). */
export default function Math({ tex, block = false }) {
  const html = useMemo(
    () => katex.renderToString(tex, { throwOnError: false, displayMode: block }),
    [tex, block]
  );
  const Tag = block ? "div" : "span";
  return <Tag className={block ? "math-block" : "math-inline"} dangerouslySetInnerHTML={{ __html: html }} />;
}
