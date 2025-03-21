import React, { useEffect, useRef, useState } from 'react';
import * as joint from 'jointjs';

// Types for diagram data
interface Participant {
  name: string;
}

interface Message {
  from: string;
  to: string;
  method: string;
  args?: any[];
  is_async?: boolean;
  is_return?: boolean;
  is_conditional?: boolean;
  condition?: string;
  code_snippet?: string;
}

export interface SequenceDiagramData {
  participants: string[];
  messages: Message[];
  title?: string;
}

interface SequenceDiagramProps {
  data: SequenceDiagramData;
  width?: number;
  height?: number;
  onElementClick?: (elementId: string) => void;
}

const SequenceDiagram: React.FC<SequenceDiagramProps> = ({
  data,
  width = 800,
  height = 600,
  onElementClick
}) => {
  const paperRef = useRef<HTMLDivElement>(null);
  const [graph, setGraph] = useState<joint.dia.Graph | null>(null);
  const [paper, setPaper] = useState<joint.dia.Paper | null>(null);

  // Initialize JointJS graph and paper
  useEffect(() => {
    if (!paperRef.current) return;

    // Create a new graph
    const newGraph = new joint.dia.Graph();

    // Create a paper with grid
    const newPaper = new joint.dia.Paper({
      el: paperRef.current,
      model: newGraph,
      width: width,
      height: height,
      gridSize: 10,
      drawGrid: true,
      background: {
        color: '#f8f9fa'
      },
      interactive: true
    });

    // Set up event handler for clicks
    if (onElementClick) {
      newPaper.on('element:pointerclick', (elementView) => {
        onElementClick(elementView.model.id);
      });
    }

    setGraph(newGraph);
    setPaper(newPaper);

    // Cleanup on unmount
    return () => {
      newGraph.clear();
      newPaper.remove();
    };
  }, [paperRef, width, height, onElementClick]);

  // Render diagram when data changes
  useEffect(() => {
    if (!graph || !data) return;

    // Clear previous diagram
    graph.clear();

    // Define namespace for sequence diagram shapes
    const namespace = joint.shapes as any;
    if (!namespace.sequence) {
      namespace.sequence = {};
    }

    // Define custom shapes for sequence diagrams
    if (!namespace.sequence.Actor) {
      // Define Actor (Participant) shape
      namespace.sequence.Actor = joint.dia.Element.extend({
        markup: [
          '<g class="rotatable">',
          '<g class="scalable">',
          '<rect class="lifeline-head-rect"/></g>',
          '<text class="lifeline-head-text"/>',
          '<line class="lifeline-line"/>',
          '</g>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Actor',
          size: { width: 100, height: 30 },
          attrs: {
            '.lifeline-head-rect': {
              fill: '#ffffff',
              stroke: '#000000',
              'stroke-width': 2,
              width: 100,
              height: 30
            },
            '.lifeline-head-text': {
              text: '',
              'font-size': 12,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': .5,
              'y-alignment': 'middle',
              fill: '#000000'
            },
            '.lifeline-line': {
              x1: 50,
              y1: 30,
              x2: 50,
              y2: 1000,
              stroke: '#000000',
              'stroke-width': 1,
              'stroke-dasharray': '5,5'
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });

      // Define Message shape
      namespace.sequence.Message = joint.dia.Link.extend({
        markup: [
          '<path class="connection" stroke="black" d="M 0 0 0 0"/>',
          '<path class="message-arrow" fill="black" stroke="black" d="M 0 0 0 0"/>',
          '<text class="message-text" font-size="12"/>',
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Message',
          attrs: {
            '.connection': {
              'stroke-width': 1,
              'stroke': '#000000'
            },
            '.message-arrow': {
              'fill': '#000000',
              'stroke': '#000000'
            },
            '.message-text': {
              'text': '',
              'font-size': 12,
              'fill': '#000000'
            }
          },
          router: { name: 'orthogonal' },
          connector: { name: 'rounded' }
        }, joint.dia.Link.prototype.defaults)
      });

      // Define Activation box shape
      namespace.sequence.Activation = joint.dia.Element.extend({
        markup: '<rect class="activation-rect"/>',
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Activation',
          size: { width: 10, height: 50 },
          attrs: {
            '.activation-rect': {
              fill: '#f5f5f5',
              stroke: '#000000',
              'stroke-width': 1,
              width: 10,
              height: 50
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });
    }

    // Render participants (actors)
    const actors: joint.dia.Element[] = [];
    const actorWidth = 100;
    const actorSpacing = 150;
    const actorY = 50;
    const lifelines: Record<string, { actor: joint.dia.Element, x: number }> = {};

    data.participants.forEach((participant, index) => {
      const x = index * actorSpacing + 100;
      
      const actor = new namespace.sequence.Actor({
        position: { x: x - (actorWidth / 2), y: actorY },
        attrs: {
          '.lifeline-head-text': { text: participant },
          '.lifeline-line': { y2: height - 50 }
        }
      });
      
      graph.addCell(actor);
      actors.push(actor);
      lifelines[participant] = { actor, x };
    });

    // Render messages
    const messageHeight = 50;
    let currentY = actorY + 50;

    data.messages.forEach((message, index) => {
      const fromLifeline = lifelines[message.from];
      const toLifeline = lifelines[message.to];
      
      if (!fromLifeline || !toLifeline) return;

      const fromX = fromLifeline.x;
      const toX = toLifeline.x;
      const isSelfMessage = message.from === message.to;
      
      // Create message link
      const messageLink = new namespace.sequence.Message({
        source: { x: fromX, y: currentY },
        target: { x: toX, y: currentY }
      });

      // Set message text
      let messageText = message.method;
      if (message.args && message.args.length > 0) {
        messageText += `(${message.args.join(', ')})`;
      }
      
      messageLink.attr({
        '.message-text': {
          text: messageText,
          'ref-y': -10
        }
      });

      // Style for different message types
      if (message.is_return) {
        messageLink.attr({
          '.connection': {
            'stroke-dasharray': '3,3'
          },
          '.message-arrow': {
            'd': 'M 0 0 L -10 5 L -10 -5 Z'
          }
        });
      } else if (message.is_async) {
        messageLink.attr({
          '.connection': {
            'stroke-dasharray': '5,2'
          }
        });
      }

      if (message.is_conditional) {
        messageLink.attr({
          '.message-text': {
            text: `[${message.condition}] ${messageText}`
          }
        });
      }

      graph.addCell(messageLink);

      // For self-messages, adjust the link routing
      if (isSelfMessage) {
        messageLink.set('vertices', [
          { x: fromX + 30, y: currentY },
          { x: fromX + 30, y: currentY + 20 },
          { x: fromX, y: currentY + 20 }
        ]);
      }

      // Increment Y for the next message
      currentY += messageHeight;
    });

    // Adjust paper size to fit the diagram
    if (paper) {
      paper.setDimensions(width, Math.max(height, currentY + 50));
    }
  }, [graph, paper, data, width, height]);

  return (
    <div className="sequence-diagram-container">
      {data.title && <h3 className="diagram-title">{data.title}</h3>}
      <div ref={paperRef} className="sequence-diagram-paper"></div>
    </div>
  );
};

export default SequenceDiagram; 