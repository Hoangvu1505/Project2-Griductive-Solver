import React from 'react';

/**
 * Procedural Vector Character Avatar Generator.
 * Creates clean, sharp, diverse SVG avatars matching Knotwise Griductive aesthetic.
 * Supports:
 * - Dedicated presets for canonical Knotwise cast (Alan, Brian, Clara, Dana, Evan, Fern, Gina, Hannah, Ivy, June, Kate, Lena, Mara, Noah, Owen, Paul, Quentin, Ruby, Sam, Tess)
 * - Deterministic procedural generation for any arbitrary name with 12 distinct hairstyles (short, long, bobs, buns, waves, spiky), 10 hair colors, 7 skin tones, collar styles, and accessories.
 */

// Knotwise canonical cast presets for exact screenshot fidelity
const CANONICAL_PRESETS = {
  alan: { skin: '#8A5232', hairColor: '#171717', hairStyle: 9, shirtColor: '#374151', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  brian: { skin: '#F5D0B5', hairColor: '#38251B', hairStyle: 0, shirtColor: '#1F2937', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  clara: { skin: '#F9DCC4', hairColor: '#E6C07B', hairStyle: 1, shirtColor: '#F3F4F6', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  dana: { skin: '#F5D0B5', hairColor: '#4A3022', hairStyle: 1, shirtColor: '#E5E7EB', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  evan: { skin: '#F9DCC4', hairColor: '#E6C07B', hairStyle: 2, shirtColor: '#4B5563', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  fern: { skin: '#F5D0B5', hairColor: '#38251B', hairStyle: 0, shirtColor: '#4B2556', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  gina: { skin: '#5E3520', hairColor: '#171717', hairStyle: 0, shirtColor: '#111827', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  hannah: { skin: '#F5D0B5', hairColor: '#171717', hairStyle: 6, shirtColor: '#1F2937', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  ivy: { skin: '#F9DCC4', hairColor: '#B3582D', hairStyle: 0, shirtColor: '#D97706', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  june: { skin: '#D49B74', hairColor: '#E6C07B', hairStyle: 7, shirtColor: '#FBBF24', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  kate: { skin: '#8A5232', hairColor: '#171717', hairStyle: 3, shirtColor: '#991B1B', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  lena: { skin: '#F9DCC4', hairColor: '#F3DEAA', hairStyle: 0, shirtColor: '#2563EB', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  mara: { skin: '#F9DCC4', hairColor: '#E6C07B', hairStyle: 1, shirtColor: '#F59E0B', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  noah: { skin: '#D49B74', hairColor: '#251A15', hairStyle: 0, shirtColor: '#374151', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  owen: { skin: '#F5D0B5', hairColor: '#4A3022', hairStyle: 0, shirtColor: '#4B5563', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  paul: { skin: '#F9DCC4', hairColor: '#5C3622', hairStyle: 0, shirtColor: '#E5E7EB', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  quentin: { skin: '#F9DCC4', hairColor: '#E6C07B', hairStyle: 0, shirtColor: '#10B981', collarStyle: 0, hasClosedEyes: true, hasGlasses: false },
  ruby: { skin: '#F9DCC4', hairColor: '#9D174D', hairStyle: 5, shirtColor: '#831843', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
  sam: { skin: '#B87B52', hairColor: '#171717', hairStyle: 0, shirtColor: '#4F46E5', collarStyle: 0, hasClosedEyes: true, hasGlasses: false },
  tess: { skin: '#F9DCC4', hairColor: '#E6C07B', hairStyle: 7, shirtColor: '#D97706', collarStyle: 0, hasClosedEyes: false, hasGlasses: false },
};

export default function Avatar({ name = '', size = 52 }) {
  const cleanName = (name || '').trim().toLowerCase();
  const preset = CANONICAL_PRESETS[cleanName];

  // Deterministic 32-bit FNV-1a hash of the name for arbitrary characters
  let hash = 2166136261;
  for (let i = 0; i < name.length; i++) {
    hash ^= name.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  const u = Math.abs(hash);

  // 1. Skin Tones
  const skinTones = [
    '#F5D0B5', // Fair peach
    '#E8B896', // Warm beige
    '#D49B74', // Golden tan
    '#B87B52', // Bronze / Caramel
    '#8A5232', // Warm rich brown
    '#5E3520', // Deep espresso
    '#F9DCC4'  // Porcelain
  ];
  const skin = preset ? preset.skin : skinTones[u % skinTones.length];

  // 2. Hair Colors
  const hairColors = [
    '#E6C07B', // Golden blonde
    '#251A15', // Dark espresso brown
    '#B3582D', // Ginger / Auburn
    '#171717', // Jet black
    '#5C3622', // Warm chestnut
    '#F3DEAA', // Platinum blonde
    '#8A2B35', // Deep burgundy
    '#9D174D', // Magenta / Ruby
    '#8D99AE', // Silver / Steel grey
    '#4A3022'  // Chocolate brown
  ];
  const hairColor = preset ? preset.hairColor : hairColors[(u >> 3) % hairColors.length];

  // 3. Shirt Colors & Collar
  const shirtColors = [
    '#3B82F6', // Royal blue
    '#10B981', // Emerald green
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#F59E0B', // Amber
    '#4B5563', // Slate grey
    '#EC4899', // Pink
    '#0D9488'  // Teal
  ];
  const shirtColor = preset ? preset.shirtColor : shirtColors[(u >> 6) % shirtColors.length];
  const collarStyle = preset ? preset.collarStyle : ((u >> 9) % 3);

  // 4. Hairstyles (12 unique styles from short to long)
  const hairStyle = preset ? preset.hairStyle : ((u >> 12) % 12);

  // 5. Facial features
  const hasGlasses = preset ? preset.hasGlasses : (((u >> 16) % 5 === 0));
  const hasClosedEyes = preset ? preset.hasClosedEyes : (((u >> 19) % 7 === 0));

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="select-none filter drop-shadow-xs"
    >
      {/* Background Soft Circle */}
      <circle cx="50" cy="50" r="48" fill="#1b1714" />

      {/* --- BACK HAIR (for long hairstyles hanging behind shoulders) --- */}
      {hairStyle === 4 && (
        // Long straight hair behind shoulders
        <path
          d="M24 38 C22 65, 23 88, 25 96 L36 96 C34 78, 33 55, 33 42 Z M76 38 C78 65, 77 88, 75 96 L64 96 C66 78, 67 55, 67 42 Z"
          fill={hairColor}
        />
      )}
      {hairStyle === 8 && (
        // Long wavy hair behind shoulders
        <path
          d="M23 38 Q18 65 24 85 Q26 92 24 96 L35 96 C33 80, 31 58, 33 42 Z M77 38 Q82 65 76 85 Q74 92 76 96 L65 96 C67 80, 69 58, 67 42 Z"
          fill={hairColor}
        />
      )}
      {hairStyle === 11 && (
        // Side-swept long hair on one side
        <path
          d="M75 36 C80 62, 78 86, 73 96 L62 96 C65 78, 66 55, 67 42 Z"
          fill={hairColor}
        />
      )}

      {/* Shoulders & Body */}
      <path
        d="M18 96 C18 76, 30 67, 50 67 C70 67, 82 76, 82 96 Z"
        fill={shirtColor}
      />

      {/* Collar details */}
      {collarStyle === 0 && (
        // Crewneck inner curve
        <path d="M42 67 C42 74, 58 74, 58 67 Z" fill={skin} />
      )}
      {collarStyle === 1 && (
        // V-neck
        <path d="M41 67 L50 78 L59 67 Z" fill={skin} />
      )}
      {collarStyle === 2 && (
        // Button-down shirt collar flaps
        <g>
          <path d="M43 67 L50 76 L57 67 Z" fill={skin} />
          <path d="M40 67 L46 76 L50 67 Z" fill="#ffffff" opacity="0.3" />
          <path d="M60 67 L54 76 L50 67 Z" fill="#ffffff" opacity="0.3" />
        </g>
      )}

      {/* Neck */}
      <rect x="44" y="55" width="12" height="14" rx="3" fill={skin} />

      {/* Ears */}
      <circle cx="29" cy="45" r="4.5" fill={skin} />
      <circle cx="71" cy="45" r="4.5" fill={skin} />

      {/* Head / Face */}
      <rect x="31" y="23" width="38" height="42" rx="19" fill={skin} />

      {/* --- EYES --- */}
      {hasClosedEyes ? (
        // Closed / Smiling eyes (like Quentin & Sam)
        <g stroke="#2C1D18" strokeWidth="2.2" strokeLinecap="round" fill="none">
          <path d="M39 44 Q43 47 47 44" />
          <path d="M53 44 Q57 47 61 44" />
        </g>
      ) : (
        // Standard round friendly eyes
        <g fill="#2C1D18">
          <circle cx="43" cy="42.5" r="2.5" />
          <circle cx="57" cy="42.5" r="2.5" />
          {/* Subtle eye gleam */}
          <circle cx="44" cy="41.5" r="0.8" fill="#FFFFFF" />
          <circle cx="58" cy="41.5" r="0.8" fill="#FFFFFF" />
        </g>
      )}

      {/* Eyebrows */}
      <path d="M39 36 Q43 34 47 36" stroke={hairColor} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M53 36 Q57 34 61 36" stroke={hairColor} strokeWidth="1.8" strokeLinecap="round" />

      {/* Subtle Nose */}
      <path d="M50 43 L48.5 48 L51.5 48" stroke={skin} strokeWidth="1.2" strokeLinecap="round" opacity="0.8" />

      {/* Smile / Mouth */}
      <path d="M45.5 53 Q50 56.5 54.5 53" stroke="#8C4A32" strokeWidth="1.6" strokeLinecap="round" fill="none" />

      {/* Glasses (optional accessory) */}
      {hasGlasses && (
        <g stroke="#374151" strokeWidth="1.6" fill="none">
          <circle cx="43" cy="42.5" r="6" />
          <circle cx="57" cy="42.5" r="6" />
          <path d="M49 42.5 L51 42.5" />
          <path d="M37 42.5 L30 41" />
          <path d="M63 42.5 L70 41" />
        </g>
      )}

      {/* --- HAIRSTYLES (12 distinct front styles) --- */}

      {/* 0: Short side-parted hair */}
      {hairStyle === 0 && (
        <path
          d="M29 36 C29 18, 44 14, 55 15 C68 16, 73 24, 71 36 C66 30, 60 24, 46 24 C36 24, 32 29, 29 36 Z"
          fill={hairColor}
        />
      )}

      {/* 1: High Bun (like Clara, Dana & Mara) */}
      {hairStyle === 1 && (
        <g>
          <circle cx="50" cy="14" r="9.5" fill={hairColor} />
          <circle cx="50" cy="14" r="5" fill="#FFFFFF" opacity="0.1" />
          <path
            d="M29 36 C29 20, 39 18, 50 18 C61 18, 71 20, 71 36 C68 28, 60 25, 50 25 C40 25, 32 28, 29 36 Z"
            fill={hairColor}
          />
        </g>
      )}

      {/* 2: Spiky short hair (like Evan) */}
      {hairStyle === 2 && (
        <path
          d="M28 35 L32 22 L38 15 L45 20 L52 13 L58 19 L66 15 L72 32 C65 24, 56 22, 45 22 C35 22, 30 28, 28 35 Z"
          fill={hairColor}
        />
      )}

      {/* 3: Curly / Voluminous afro (like Kate) */}
      {hairStyle === 3 && (
        <g fill={hairColor}>
          <circle cx="34" cy="24" r="8" />
          <circle cx="50" cy="18" r="9" />
          <circle cx="66" cy="24" r="8" />
          <circle cx="28" cy="33" r="7" />
          <circle cx="72" cy="33" r="7" />
          <path d="M29 38 C28 22, 40 19, 50 19 C60 19, 72 22, 71 38 C67 29, 60 25, 50 25 C40 25, 33 29, 29 38 Z" />
        </g>
      )}

      {/* 4: Long straight hair front bangs */}
      {hairStyle === 4 && (
        <path
          d="M29 45 C28 22, 40 17, 50 17 C60 17, 72 22, 71 45 C68 30, 60 24, 50 24 C40 24, 32 30, 29 45 Z"
          fill={hairColor}
        />
      )}

      {/* 5: Bob cut with bangs (like Ruby) */}
      {hairStyle === 5 && (
        <path
          d="M27 48 C27 22, 38 16, 50 16 C62 16, 73 22, 73 48 C71 34, 66 26, 58 26 C54 30, 46 30, 42 26 C34 26, 29 34, 27 48 Z"
          fill={hairColor}
        />
      )}

      {/* 6: High Ponytail (like Hannah) */}
      {hairStyle === 6 && (
        <g>
          {/* Ponytail tie and tail */}
          <ellipse cx="50" cy="14" rx="4" ry="7" fill={hairColor} transform="rotate(25 50 14)" />
          <path d="M52 14 Q65 16 68 26 Q64 30 56 22 Z" fill={hairColor} />
          {/* Front swept hair */}
          <path
            d="M29 36 C29 20, 39 17, 50 17 C61 17, 71 20, 71 36 C68 27, 60 23, 50 23 C40 23, 32 27, 29 36 Z"
            fill={hairColor}
          />
        </g>
      )}

      {/* 7: Space Buns (like June & Tess) */}
      {hairStyle === 7 && (
        <g>
          <circle cx="34" cy="15" r="7" fill={hairColor} />
          <circle cx="66" cy="15" r="7" fill={hairColor} />
          <path
            d="M29 36 C29 20, 39 18, 50 18 C61 18, 71 20, 71 36 C67 27, 58 24, 50 24 C42 24, 33 27, 29 36 Z"
            fill={hairColor}
          />
        </g>
      )}

      {/* 8: Long wavy hair front waves */}
      {hairStyle === 8 && (
        <path
          d="M28 46 Q31 32 38 27 Q44 23 50 23 Q56 23 62 27 Q69 32 72 46 C68 33, 62 25, 50 25 C38 25, 32 33, 28 46 Z"
          fill={hairColor}
        />
      )}

      {/* 9: Clean Buzzcut / Fade (like Alan) */}
      {hairStyle === 9 && (
        <path
          d="M30 32 C30 20, 40 18, 50 18 C60 18, 70 20, 70 32 C68 25, 60 22, 50 22 C40 22, 32 25, 30 32 Z"
          fill={hairColor}
          opacity="0.9"
        />
      )}

      {/* 10: Middle-part curtains */}
      {hairStyle === 10 && (
        <path
          d="M28 40 C28 20, 42 16, 49 17 L50 26 C44 26, 36 30, 34 40 Z M72 40 C72 20, 58 16, 51 17 L50 26 C56 26, 64 30, 66 40 Z"
          fill={hairColor}
        />
      )}

      {/* 11: Side-swept with cute clip */}
      {hairStyle === 11 && (
        <g>
          <path
            d="M28 38 C28 19, 44 15, 56 16 C69 17, 73 26, 72 46 C67 33, 60 25, 46 25 C35 25, 31 31, 28 38 Z"
            fill={hairColor}
          />
          {/* Small decorative hair clip */}
          <rect x="36" y="27" width="7" height="2.5" rx="1.2" fill="#F59E0B" transform="rotate(-15 36 27)" />
        </g>
      )}
    </svg>
  );
}
