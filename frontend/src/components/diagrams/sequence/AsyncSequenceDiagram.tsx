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
  is_awaited?: boolean;
  suspend_point?: boolean;
  condition?: string;
  code_snippet?: string;
  track?: string;
  creates_track?: string;
  returns_to_track?: string;
}

interface ExecutionTrack {
  [key: string]: number[];
}

export interface AsyncSequenceDiagramData {
  participants: string[];
  messages: Message[];
  execution_tracks: ExecutionTrack;
  title?: string;
}

interface AsyncSequenceDiagramProps {
  data: AsyncSequenceDiagramData;
  width?: number;
  height?: number;
  onElementClick?: (elementId: string) => void;
}

const AsyncSequenceDiagram: React.FC<AsyncSequenceDiagramProps> = ({
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

      // Define Message shape with enhanced styling for async patterns
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
      
      // Define AsyncBoundary shape (for showing async execution regions)
      namespace.sequence.AsyncBoundary = joint.dia.Element.extend({
        markup: [
          '<rect class="async-region-rect"/>',
          '<text class="async-region-text"/>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.AsyncBoundary',
          size: { width: 150, height: 30 },
          attrs: {
            '.async-region-rect': {
              fill: 'rgba(200, 230, 255, 0.2)',
              stroke: '#4da6ff',
              'stroke-dasharray': '5,3',
              'stroke-width': 1.5,
              rx: 5,
              ry: 5,
              width: 150,
              height: 30
            },
            '.async-region-text': {
              text: 'Async',
              'font-size': 10,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': 12,
              fill: '#4da6ff'
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

    // Track execution contexts for visualizing parallel execution
    const executionTracks: Record<string, {
      y: number,
      messages: Message[],
      regions: { startY: number, endY: number, name: string }[]
    }> = {};
    
    // Initialize the main track
    executionTracks['main'] = { 
      y: actorY + 50, 
      messages: [],
      regions: []
    };
    
    // Group messages by track
    for (const trackName in data.execution_tracks) {
      const messageIndices = data.execution_tracks[trackName];
      const trackMessages = messageIndices.map(idx => data.messages[idx]);
      
      executionTracks[trackName] = {
        y: actorY + 50,  // Will be adjusted during rendering
        messages: trackMessages,
        regions: []
      };
    }
    
    // Calculate vertical positions for each track
    let nextY = actorY + 50;
    const messageHeight = 50;
    const trackSpacing = 20;
    
    Object.keys(executionTracks).forEach(trackName => {
      executionTracks[trackName].y = nextY;
      
      // Reserve space for this track's messages
      const trackHeight = executionTracks[trackName].messages.length * messageHeight;
      nextY += trackHeight + trackSpacing;
    });
    
    // Render messages for each track
    for (const trackName in executionTracks) {
      const track = executionTracks[trackName];
      let currentY = track.y;
      let regionStartY = 0;
      let currentRegion = '';
      
      // Render messages for this track
      track.messages.forEach((message, index) => {
        const fromLifeline = lifelines[message.from];
        const toLifeline = lifelines[message.to];
        
        if (!fromLifeline || !toLifeline) return;

        const fromX = fromLifeline.x;
        const toX = toLifeline.x;
        const isSelfMessage = message.from === message.to;
        
        // Start a new region for async execution contexts
        if (message.creates_track) {
          regionStartY = currentY;
          currentRegion = message.creates_track;
        }
        
        // End a region when returning to a previous track
        if (message.returns_to_track) {
          if (currentRegion) {
            track.regions.push({
              startY: regionStartY,
              endY: currentY + messageHeight,
              name: currentRegion
            });
            currentRegion = '';
          }
        }
        
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
              'stroke-dasharray': '3,3',
              'stroke': '#666666'
            },
            '.message-arrow': {
              'fill': '#666666',
              'stroke': '#666666'
            },
            '.message-text': {
              'fill': '#666666'
            }
          });
        }
        
        // Style for asynchronous messages
        if (message.is_async) {
          messageLink.attr({
            '.connection': {
              'stroke-dasharray': '5,2',
              'stroke': '#3771c8'
            },
            '.message-arrow': {
              'fill': '#3771c8',
              'stroke': '#3771c8'
            },
            '.message-text': {
              'fill': '#3771c8'
            }
          });
        }
        
        // Style for awaited messages
        if (message.is_awaited) {
          messageLink.attr({
            '.connection': {
              'stroke-width': 2,
              'stroke': '#6c2dc7'
            },
            '.message-arrow': {
              'fill': '#6c2dc7',
              'stroke': '#6c2dc7'
            },
            '.message-text': {
              'fill': '#6c2dc7',
              'font-weight': 'bold'
            }
          });
        }
        
        // Style for conditional messages
        if (message.is_conditional) {
          messageLink.attr({
            '.connection': {
              'stroke': '#d83931'
            },
            '.message-arrow': {
              'fill': '#d83931',
              'stroke': '#d83931'
            },
            '.message-text': {
              'text': `[${message.condition}] ${messageText}`,
              'fill': '#d83931'
            }
          });
        }
        
        // Add to graph
        graph.addCell(messageLink);
        
        // Update current Y position for next message
        currentY += messageHeight;
      });
      
      // Close any open regions at the end of the track
      if (currentRegion) {
        track.regions.push({
          startY: regionStartY,
          endY: currentY,
          name: currentRegion
        });
      }
      
      // Render async regions for this track
      track.regions.forEach(region => {
        const trackWidth = (data.participants.length - 1) * actorSpacing + 150;
        
        const asyncRegion = new namespace.sequence.AsyncBoundary({
          position: { x: 50, y: region.startY - 15 },
          size: { width: trackWidth, height: region.endY - region.startY + 30 },
          attrs: {
            '.async-region-text': { 
              text: region.name.charAt(0).toUpperCase() + region.name.slice(1) 
            }
          }
        });
        
        // Add to graph behind other elements
        graph.addCell(asyncRegion);
        asyncRegion.toBack();
      });
    }

  }, [graph, data, height]);

  return (
    <div className="async-sequence-diagram">
      <div ref={paperRef} className="diagram-paper" style={{ width, height }} />
    </div>
  );
};

export default AsyncSequenceDiagram; 